import os
from xml.dom.minidom import Document

import pwd

from core import logger
from core.coreobj import PyCoreNet
from core.coreobj import PyCoreNode
from core.enumerations import RegisterTlvs, EventTypes
from core.xml import xmlutils


class CoreDocumentWriter0(Document):
    """
    Utility class for writing a CoreSession to XML. The init method builds
    an xml.dom.minidom.Document, and the writexml() method saves the XML file.
    """

    def __init__(self, session):
        """
        Create an empty Scenario XML Document, then populate it with
        objects from the given session.
        """
        Document.__init__(self)
        self.session = session
        self.scenario = self.createElement("Scenario")
        self.np = self.createElement("NetworkPlan")
        self.mp = self.createElement("MotionPlan")
        self.sp = self.createElement("ServicePlan")
        self.meta = self.createElement("CoreMetaData")

        self.appendChild(self.scenario)
        self.scenario.appendChild(self.np)
        self.scenario.appendChild(self.mp)
        self.scenario.appendChild(self.sp)
        self.scenario.appendChild(self.meta)

        self.populatefromsession()

    def populatefromsession(self):
        if self.session.state != EventTypes.RUNTIME_STATE.value:
            self.session.emane.setup()  # not during runtime?
        self.addorigin()
        self.adddefaultservices()
        self.addnets()
        self.addnodes()
        self.addmetadata()

    def writexml(self, filename):
        logger.info("saving session XML file %s", filename)
        f = open(filename, "w")
        Document.writexml(self, writer=f, indent="", addindent="  ", newl="\n", encoding="UTF-8")
        f.close()
        if self.session.user is not None:
            uid = pwd.getpwnam(self.session.user).pw_uid
            gid = os.stat(self.session.sessiondir).st_gid
            os.chown(filename, uid, gid)

    def addnets(self):
        """
        Add PyCoreNet objects as NetworkDefinition XML elements.
        """
        with self.session._objects_lock:
            for net in self.session.objects.itervalues():
                if not isinstance(net, PyCoreNet):
                    continue
                self.addnet(net)

    def addnet(self, net):
        """
        Add one PyCoreNet object as a NetworkDefinition XML element.
        """
        n = self.createElement("NetworkDefinition")
        self.np.appendChild(n)
        n.setAttribute("name", net.name)
        # could use net.brname
        n.setAttribute("id", "%s" % net.objid)
        n.setAttribute("type", "%s" % net.__class__.__name__)
        self.addnetinterfaces(n, net)
        # key used with tunnel node
        if hasattr(net, 'grekey') and net.grekey is not None:
            n.setAttribute("key", "%s" % net.grekey)
        # link parameters
        for netif in net.netifs(sort=True):
            self.addnetem(n, netif)
            # wireless/mobility models
        modelconfigs = net.session.mobility.get_models(net)
        modelconfigs += net.session.emane.get_models(net)
        self.addmodels(n, modelconfigs)
        self.addposition(net)

    def addnetem(self, n, netif):
        """
        Similar to addmodels(); used for writing netem link effects
        parameters. TODO: Interface parameters should be moved to the model
        construct, then this separate method shouldn't be required.
        """
        params = netif.getparams()
        if len(params) == 0:
            return
        model = self.createElement("model")
        model.setAttribute("name", "netem")
        model.setAttribute("netif", netif.name)
        if hasattr(netif, "node") and netif.node is not None:
            model.setAttribute("peer", netif.node.name)
        # link between switches uses one veth interface
        elif hasattr(netif, "othernet") and netif.othernet is not None:
            if netif.othernet.name == n.getAttribute("name"):
                model.setAttribute("peer", netif.net.name)
            else:
                model.setAttribute("peer", netif.othernet.name)
                model.setAttribute("netif", netif.localname)
            # hack used for upstream parameters for link between switches
            # (see LxBrNet.linknet())
            if netif.othernet.objid == int(n.getAttribute("id")):
                netif.swapparams('_params_up')
                params = netif.getparams()
                netif.swapparams('_params_up')
        has_params = False
        for k, v in params:
            # default netem parameters are 0 or None
            if v is None or v == 0:
                continue
            if k == "has_netem" or k == "has_tbf":
                continue
            key = self.createElement(k)
            key.appendChild(self.createTextNode("%s" % v))
            model.appendChild(key)
            has_params = True
        if has_params:
            n.appendChild(model)

    def addmodels(self, n, configs):
        """
        Add models from a list of model-class, config values tuples.
        """
        for m, conf in configs:
            model = self.createElement("model")
            n.appendChild(model)
            model.setAttribute("name", m.name)
            type = "wireless"
            if m.config_type == RegisterTlvs.MOBILITY.value:
                type = "mobility"
            model.setAttribute("type", type)

            for k, value in conf.iteritems():
                key = self.createElement(k)
                if value is None:
                    value = ""
                key.appendChild(self.createTextNode("%s" % value))
                model.appendChild(key)

    def addnodes(self):
        """
        Add PyCoreNode objects as node XML elements.
        """
        with self.session._objects_lock:
            for node in self.session.objects.itervalues():
                if not isinstance(node, PyCoreNode):
                    continue
                self.addnode(node)

    def addnode(self, node):
        """
        Add a PyCoreNode object as node XML elements.
        """
        n = self.createElement("Node")
        self.np.appendChild(n)
        n.setAttribute("name", node.name)
        n.setAttribute("id", "%s" % node.objid)
        if node.type:
            n.setAttribute("type", node.type)
        self.addinterfaces(n, node)
        self.addposition(node)
        xmlutils.add_param_to_parent(self, n, "icon", node.icon)
        xmlutils.add_param_to_parent(self, n, "canvas", node.canvas)
        self.addservices(node)

    def addinterfaces(self, n, node):
        """
        Add PyCoreNetIfs to node XML elements.
        """
        for ifc in node.netifs(sort=True):
            i = self.createElement("interface")
            n.appendChild(i)
            i.setAttribute("name", ifc.name)
            netmodel = None
            if ifc.net:
                i.setAttribute("net", ifc.net.name)
                if hasattr(ifc.net, "model"):
                    netmodel = ifc.net.model
            if ifc.mtu and ifc.mtu != 1500:
                i.setAttribute("mtu", "%s" % ifc.mtu)
            # could use ifc.params, transport_type
            self.addaddresses(i, ifc)
            # per-interface models
            if netmodel and netmodel.name[:6] == "emane_":
                cfg = self.session.emane.getifcconfig(node.objid, ifc, netmodel.name)
                if cfg:
                    self.addmodels(i, ((netmodel, cfg),))

    def addnetinterfaces(self, n, net):
        """
        Similar to addinterfaces(), but only adds interface elements to the
        supplied XML node that would not otherwise appear in the Node elements.
        These are any interfaces that link two switches/hubs together.
        """
        for ifc in net.netifs(sort=True):
            if not hasattr(ifc, "othernet") or not ifc.othernet:
                continue
            i = self.createElement("interface")
            n.appendChild(i)
            if net.objid == ifc.net.objid:
                i.setAttribute("name", ifc.localname)
                i.setAttribute("net", ifc.othernet.name)
            else:
                i.setAttribute("name", ifc.name)
                i.setAttribute("net", ifc.net.name)

    def addposition(self, node):
        """
        Add object coordinates as location XML element.
        """
        (x, y, z) = node.position.get()
        if x is None or y is None:
            return
        # <Node name="n1">
        mpn = self.createElement("Node")
        mpn.setAttribute("name", node.name)
        self.mp.appendChild(mpn)

        #   <motion type="stationary">
        motion = self.createElement("motion")
        motion.setAttribute("type", "stationary")
        mpn.appendChild(motion)

        #       <point>$X$,$Y$,$Z$</point>
        pt = self.createElement("point")
        motion.appendChild(pt)
        coordstxt = "%s,%s" % (x, y)
        if z:
            coordstxt += ",%s" % z
        coords = self.createTextNode(coordstxt)
        pt.appendChild(coords)

    def addorigin(self):
        """
        Add origin to Motion Plan using canvas reference point.
        The CoreLocation class maintains this reference point.
        """
        refgeo = self.session.location.refgeo
        origin = self.createElement("origin")
        attrs = ("lat", "lon", "alt")
        have_origin = False
        for i in xrange(3):
            if refgeo[i] is not None:
                origin.setAttribute(attrs[i], str(refgeo[i]))
                have_origin = True
        if not have_origin:
            return
        if self.session.location.refscale != 1.0:  # 100 pixels = refscale m
            origin.setAttribute("scale100", str(self.session.location.refscale))
        if self.session.location.refxyz != (0.0, 0.0, 0.0):
            pt = self.createElement("point")
            origin.appendChild(pt)
            x, y, z = self.session.location.refxyz
            coordstxt = "%s,%s" % (x, y)
            if z:
                coordstxt += ",%s" % z
            coords = self.createTextNode(coordstxt)
            pt.appendChild(coords)

        self.mp.appendChild(origin)

    def adddefaultservices(self):
        """
        Add default services and node types to the ServicePlan.
        """
        for type in self.session.services.default_services:
            defaults = self.session.services.get_default_services(type)
            spn = self.createElement("Node")
            spn.setAttribute("type", type)
            self.sp.appendChild(spn)
            for svc in defaults:
                s = self.createElement("Service")
                spn.appendChild(s)
                s.setAttribute("name", str(svc.name))

    def addservices(self, node):
        """
        Add services and their customizations to the ServicePlan.
        """
        if len(node.services) == 0:
            return
        defaults = self.session.services.get_default_services(node.type)
        if node.services == defaults:
            return
        spn = self.createElement("Node")
        spn.setAttribute("name", node.name)
        self.sp.appendChild(spn)

        for svc in node.services:
            s = self.createElement("Service")
            spn.appendChild(s)
            s.setAttribute("name", str(svc.name))
            # only record service names if not a customized service
            if not svc.custom:
                continue
            s.setAttribute("custom", str(svc.custom))
            xmlutils.add_elements_from_list(self, s, svc.dirs, "Directory", "name")

            for fn in svc.configs:
                if len(fn) == 0:
                    continue
                f = self.createElement("File")
                f.setAttribute("name", fn)
                # all file names are added to determine when a file has been deleted
                s.appendChild(f)
                data = svc.config_data.get(fn)
                if data is None:
                    # this includes only customized file contents and skips
                    # the auto-generated files
                    continue
                txt = self.createTextNode(data)
                f.appendChild(txt)

            xmlutils.add_text_elements_from_list(self, s, svc.startup, "Command", (("type", "start"),))
            xmlutils.add_text_elements_from_list(self, s, svc.shutdown, "Command", (("type", "stop"),))
            xmlutils.add_text_elements_from_list(self, s, svc.validate, "Command", (("type", "validate"),))

    def addaddresses(self, i, netif):
        """
        Add MAC and IP addresses to interface XML elements.
        """
        if netif.hwaddr:
            h = self.createElement("address")
            i.appendChild(h)
            h.setAttribute("type", "mac")
            htxt = self.createTextNode("%s" % netif.hwaddr)
            h.appendChild(htxt)
        for addr in netif.addrlist:
            a = self.createElement("address")
            i.appendChild(a)
            # a.setAttribute("type", )
            atxt = self.createTextNode("%s" % addr)
            a.appendChild(atxt)

    def addhooks(self):
        """
        Add hook script XML elements to the metadata tag.
        """
        hooks = self.createElement("Hooks")
        for state in sorted(self.session._hooks.keys()):
            for filename, data in self.session._hooks[state]:
                hook = self.createElement("Hook")
                hook.setAttribute("name", filename)
                hook.setAttribute("state", str(state))
                txt = self.createTextNode(data)
                hook.appendChild(txt)
                hooks.appendChild(hook)
        if hooks.hasChildNodes():
            self.meta.appendChild(hooks)

    def addmetadata(self):
        """
        Add CORE-specific session meta-data XML elements.
        """
        # options
        options = self.createElement("SessionOptions")
        defaults = self.session.options.default_values()
        for name, current_value in self.session.options.get_configs().iteritems():
            default_value = defaults[name]
            if current_value != default_value:
                xmlutils.add_text_param_to_parent(self, options, name, current_value)

        if options.hasChildNodes():
            self.meta.appendChild(options)

        # hook scripts
        self.addhooks()

        # meta
        meta = self.createElement("MetaData")
        self.meta.appendChild(meta)
        for name, current_value in self.session.metadata.get_configs().iteritems():
            xmlutils.add_text_param_to_parent(self, meta, name, current_value)
