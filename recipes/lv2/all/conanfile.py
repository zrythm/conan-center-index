from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=1.53.0"

# Extensions installed under the URI-style path lv2/lv2plug.in/ns/ext
EXTENSION_NAMES = [
    "atom",
    "buf-size",
    "data-access",
    "dynmanifest",
    "event",
    "instance-access",
    "log",
    "midi",
    "morph",
    "options",
    "parameters",
    "patch",
    "port-groups",
    "port-props",
    "presets",
    "resize-port",
    "state",
    "time",
    "uri-map",
    "urid",
    "worker",
]

# Extensions installed under the URI-style path lv2/lv2plug.in/ns/extensions
EXTENSIONS_NAMES = [
    "ui",
    "units",
]


class Lv2Conan(ConanFile):
    name = "lv2"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://lv2plug.in/"
    description = "The LV2 plugin standard: headers and specification data bundles"
    topics = "audio", "plugins", "specification"
    license = "ISC"

    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def package(self):
        src = self.source_folder
        pkg = self.package_folder
        inc = os.path.join(pkg, "include")
        ns = os.path.join(inc, "lv2", "lv2plug.in", "ns")

        copy(self, "COPYING", src=src, dst=os.path.join(pkg, "licenses"))

        # Unified API headers at include/lv2/<extension>/<extension>.h
        copy(self, "*.h", src=os.path.join(src, "include"), dst=inc)
        # The core lv2.h is also installed at the top include level
        copy(self, "lv2.h", src=os.path.join(src, "include", "lv2", "core"), dst=inc)

        # Backwards compatible headers at URI-style paths
        copy(self, "*", src=os.path.join(src, "include", "lv2", "core"), dst=os.path.join(ns, "lv2core"))
        for ext_name in EXTENSION_NAMES + EXTENSIONS_NAMES:
            group = "ext" if ext_name in EXTENSION_NAMES else "extensions"
            copy(self, "*.h", src=os.path.join(src, "include", "lv2", ext_name), dst=os.path.join(ns, group, ext_name))

        # Specification data bundles are runtime resources, not libraries
        copy(self, "*", src=os.path.join(src, "lv2"), dst=os.path.join(pkg, "res", "lv2"))
        copy(self, "*.ttl", src=os.path.join(src, "schemas.lv2"), dst=os.path.join(pkg, "res", "lv2", "schemas.lv2"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "lv2")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.resdirs = ["res"]
