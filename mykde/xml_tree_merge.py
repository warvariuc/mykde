__author__ = 'Victor Varvaryuk <victor.varvariuc@gmail.com>'

import os
import xml.etree.ElementTree as et


class NodeMismatchError(Exception):
    """
    """


_orig_namespace_map = et.register_namespace._namespace_map


# TODO: somehow keep destination namespace names
class XmlTreeMerger():
    """Class for merging an XML tree into another XML tree.
    """
    def _is_node_match(self, src_node, dst_node):
        """Return True if `src_node` matches `dst_node`, i.e. tag names are equal and
        attribute names and values of `src_node` are a subset of `dst_node`s attributes.
        src_node='<kpartgui name="konsole">' is considered a matching node for
        dst_node='<kpartgui name="konsole" version="10">', but not for
        dst_node='<kpartgui name="konsole" version="11">'.
        """
        return (src_node.tag == dst_node.tag and
                all(item in dst_node.attrib.items() for item in src_node.attrib.items()))

    def merge(self, src_path, dst_path, indent=2):
        """Merge XML file on `src_path` into XML file on `dst_path`.
        """
        et.register_namespace._namespace_map = _orig_namespace_map
        for event, elem in et.iterparse(src_path, ("start-ns",)):
            et.register_namespace(*elem)
        src_tree = et.parse(src_path)
        if not os.path.isfile(dst_path):
            # if destination XML file does not exist use source XML
            # i.e. after merge destination will be equal to source
            dst_path = src_path
        dst_tree = et.parse(dst_path)

        if not self._is_node_match(src_tree.getroot(), dst_tree.getroot()):
            raise NodeMismatchError('Root nodes do not match')
        self._update_node(src_tree.getroot(), dst_tree.getroot())
        # self._indent(dst_tree.getroot(), indent=indent)
        return dst_tree

    def _update_node(self, src_node, dst_node):
        """Recursively update `dst_node` with tag and attributes of `src_node`.
        """
        dst_node.text = src_node.text
        for src_child_node in src_node:
            for dst_child_node in dst_node:
                if self._is_node_match(src_child_node, dst_child_node):
                    break  # matching node found
            else:  # matching child node not found - create one
                dst_child_node = et.SubElement(dst_node, src_child_node.tag, src_child_node.attrib)
            self._update_node(src_child_node, dst_child_node)

    def _indent(self, elem, level=0, indent=2):
        """In-place recursively indent tree nodes.
        """
        i = "\n" + level * " " * indent
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and not (elem.tail and elem.tail.strip()):
                elem.tail = i
