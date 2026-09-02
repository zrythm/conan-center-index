#include <zix/allocator.h>

int main() {
    return zix_default_allocator() ? 0 : 1;
}
