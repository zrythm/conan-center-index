from conan import ConanFile
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=1.53.0"


class SordConan(ConanFile):
    name = "sord"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://drobilla.net/software/sord.html"
    description = "A lightweight C library for storing RDF data in memory"
    topics = "linked-data", "semantic-web", "rdf"
    license = "ISC"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }
    exports_sources = "CMakeLists.txt"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        self.settings.rm_safe("compiler.cppstd")
        self.settings.rm_safe("compiler.libcxx")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        self.requires("serd/0.32.10", transitive_headers=True)
        self.requires("zix/0.8.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        copy(self, "CMakeLists.txt", self.export_sources_folder, self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)

    def package_info(self):
        self.cpp_info.set_property("pkg_config_name", "sord-0")
        self.cpp_info.libs = ["sord-0"]
        self.cpp_info.includedirs = [os.path.join("include", "sord-0")]
        if self.settings.os == "Windows" and not self.options.shared:
            self.cpp_info.defines.append("SORD_STATIC")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs.append("m")
