<script setup>
defineProps({
    frame: { type: String, default: null },
    locked: { type: Boolean, default: false },
})
</script>

<template>
    <span class="avatar-frame" :class="[frame, { locked }]" aria-hidden="true"></span>
</template>

<style scoped>
.avatar-frame {
    position: absolute;
    inset: -4px;
    border: 4px solid transparent;
    border-radius: 50%;
    pointer-events: none;
    z-index: 1;
}

.bronze {
    border-color: #b87333;
    box-shadow: 0 0 0 1px #8c4f20, inset 0 0 0 1px #edc39a;
}

.silver {
    border-color: #b8c2cc;
    box-shadow: 0 0 0 1px #7d8996, inset 0 0 0 1px #f0f4f8;
}

.gold {
    border-color: #e2b238;
    box-shadow: 0 0 0 1px #aa7c16, inset 0 0 0 1px #fff0ac;
}

.locked {
    border-color: #d1d5db;
    box-shadow: none;
}
</style>
