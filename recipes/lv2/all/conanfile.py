from conan import ConanFile
from conan.tools.env import VirtualBuildEnv
from conan.tools.files import copy, get, mkdir, rename, rmdir
from conan.tools.layout import basic_layout
from conan.tools.meson import Meson, MesonToolchain
import os

required_conan_version = ">=1.53.0"


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

    def build_requirements(self):
        self.tool_requires("meson/1.10.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        env = VirtualBuildEnv(self)
        env.generate()
        tc = MesonToolchain(self)
        tc.project_options["docs"] = "disabled"
        tc.project_options["online_docs"] = "false"
        tc.project_options["plugins"] = "disabled"
        tc.project_options["tests"] = "disabled"
        tc.generate()

    def build(self):
        meson = Meson(self)
        meson.configure()
        meson.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        meson = Meson(self)
        meson.install()
        rmdir(self, os.path.join(self.package_folder, "bin"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # Specification data bundles are runtime resources, not libraries
        mkdir(self, os.path.join(self.package_folder, "res"))
        rename(self, os.path.join(self.package_folder, "lib", "lv2"),
               os.path.join(self.package_folder, "res", "lv2"))

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "lv2")
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.resdirs = ["res"]
