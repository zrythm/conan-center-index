#include <lilv/lilv.h>

int main() {
    LilvWorld* world = lilv_world_new();
    if (!world) {
        return 1;
    }
    lilv_world_free(world);
    return 0;
}
