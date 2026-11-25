import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.apple import fix_apple_shared_install_name
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get, rmdir
from conan.tools.microsoft import is_msvc

required_conan_version = ">=2.0.0"


class QtmcpConan(ConanFile):
    name = "qtmcp"
    description = "Qt implementation of the Model Context Protocol (MCP)"
    license = "LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only"
    url = "https://gitlab.zrythm.org/zrythm/conan-center-index"
    homepage = "https://github.com/signal-slot/qtmcp"
    topics = ("mcp", "model-context-protocol", "qt")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # Build ARM64EC machine code for a consumer that is itself ARM64EC,
        # in an otherwise x86_64 dependency graph.
        "arm64ec": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "arm64ec": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # QtMcp public headers expose QtCore and QtNetwork types, so
        # consumers need the Qt headers and libraries too.
        self.requires(
            "qt/[>=6.8 <7]", transitive_headers=True, transitive_libs=True
        )

    def validate(self):
        check_min_cppstd(self, 20)
        if self.options.arm64ec and (
            self.settings.get_safe("os") != "Windows"
            or not is_msvc(self)
            or self.settings.get_safe("arch") not in ("x86_64", "arm64ec")
        ):
            raise ConanInvalidConfiguration(
                "arm64ec=True requires os=Windows, compiler=msvc and "
                "arch=x86_64 or arch=arm64ec"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        if self.options.arm64ec:
            # CMake also sees this flag during compiler identification and
            # then adds /MACHINE:ARM64EC and the _ARM64EC_ define itself.
            tc.extra_cflags.append("/arm64EC")
            tc.extra_cxxflags.append("/arm64EC")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()
        fix_apple_shared_install_name(self)
        # CMakeDeps generates its own QtMcp config files from cpp_info.
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "QtMcp")
        # The three exported CMake targets QtMcp::Common, QtMcp::Server and
        # QtMcp::StreamableHttp map to the McpCommon, McpServer and
        # McpServerStreamableHttp libraries installed by the project.
        common = self.cpp_info.components["common"]
        common.set_property("cmake_target_name", "QtMcp::Common")
        common.libs = ["McpCommon"]
        common.requires = ["qt::qtCore"]

        server = self.cpp_info.components["server"]
        server.set_property("cmake_target_name", "QtMcp::Server")
        server.libs = ["McpServer"]
        server.requires = ["common", "qt::qtCore", "qt::qtNetwork"]

        streamable_http = self.cpp_info.components["streamablehttp"]
        streamable_http.set_property("cmake_target_name", "QtMcp::StreamableHttp")
        streamable_http.libs = ["McpServerStreamableHttp"]
        streamable_http.requires = ["server", "qt::qtCore", "qt::qtNetwork"]
