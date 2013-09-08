import os
import xml.etree.ElementTree as ET


class XmlTreeMerger():
    """Class for merging an XML tree into another XML tree.
    """
    def __init__(self, path, patch_path):
        self.patch_tree = ET.parse(patch_path)
        if not os.path.isfile(path):
            # if destination XML file does not exist use source XML
            # i.e. after merge destination will be equal to source
            path = patch_path
        self.tree = ET.parse(path)

    def matches(self, patch_node, node):
        """Return True if `node_patch` matches `node`, i.e. tag names are equal and
        attribute names and values of `node_patch` are subset of attributes of `node`.
        <kpartgui name="konsole"> is considered the same node as
        <kpartgui name="konsole" version="10">, while
        <kpartgui name="konsole" version="11"> is not.
        """
        return (patch_node.tag == node.tag
                and all(item in node.attrib.items()
                        for item in patch_node.attrib.items()))

    def merge(self):
        """Merge `patch_tree` into `tree`.
        """
        root = self.tree.getroot()
        patch_root = self.patch_tree.getroot()
        if not self.matches(patch_root, root):
            raise Exception('Root nodes do not match')
        self.patch(root, patch_root)
        self.indent(root)
        return ET.tostring(root, encoding='unicode')

    def patch(self, node, patch_node):
        for patch_child_node in patch_node:
            for child_node in node:
                if self.matches(patch_child_node, child_node):
                    # matching node found
                    break
            else:
                # matching node not found - create one
                child_node = ET.SubElement(node, patch_child_node.tag, patch_child_node.attrib)
            self.patch(child_node, patch_child_node)

    def indent(self, elem, level=0):
        """In-place prettyprint formatter.
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
