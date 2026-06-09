<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup>
</script>

<style>
:root {
  --bg: #f5f7f8;
  --panel: #ffffff;
  --panel-soft: #f9faf7;
  --line: #dfe6e2;
  --line-strong: #c8d4cf;
  --text: #1b2623;
  --muted: #66746f;
  --faint: #8b9894;
  --green: #217a61;
  --green-dark: #145a48;
  --green-soft: #e4f2ec;
  --blue: #2769a8;
  --blue-soft: #e7f0f8;
  --amber: #b36a17;
  --amber-soft: #fff2dc;
  --red: #b93d35;
  --red-soft: #ffe8e5;
  --ink: #283733;
  --shadow: 0 18px 50px rgba(32, 51, 45, .08);
  --sidebar-bg: #182722;
  --sidebar-text: #eef5f1;
  --sidebar-muted: #b9cac3;
  --sidebar-faint: #a9bcb4;
  font-family: "Inter", "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  letter-spacing: 0;
  font-family: "Inter", "PingFang SC", "Microsoft YaHei", Arial, sans-serif;
}

#app {
  min-height: 100vh;
}

button,
input,
select,
textarea {
  font: inherit;
}

button {
  border: 0;
  cursor: pointer;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--line-strong);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--faint);
}

/* Shared button styles matching prototype */
.btn {
  min-height: 38px;
  border-radius: 7px;
  padding: 0 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--ink);
  background: #eef3f0;
  border: 1px solid var(--line);
  white-space: nowrap;
  font-size: 14px;
  transition: all 0.15s;
}

.btn:hover {
  border-color: var(--line-strong);
  background: #e6eee9;
}

.btn.primary {
  color: #ffffff;
  background: var(--green);
  border-color: var(--green);
}

.btn.primary:hover {
  background: var(--green-dark);
  border-color: var(--green-dark);
}

.btn.danger {
  color: var(--red);
  background: var(--red-soft);
  border-color: #f4c8c3;
}

.btn.danger:hover {
  background: #fdd9d4;
}

.btn.icon-only {
  width: 38px;
  padding: 0;
}

/* Status badges */
.status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  border-radius: 999px;
  padding: 0 9px;
  font-size: 12px;
  white-space: nowrap;
  font-weight: 500;
}

.status.pending {
  color: var(--amber);
  background: var(--amber-soft);
}

.status.approved {
  color: var(--green-dark);
  background: var(--green-soft);
}

.status.rejected {
  color: var(--red);
  background: var(--red-soft);
}

.status.published {
  color: var(--blue);
  background: var(--blue-soft);
}

/* Element Plus overrides */
.el-button--primary {
  --el-button-bg-color: var(--green);
  --el-button-border-color: var(--green);
  --el-button-hover-bg-color: var(--green-dark);
  --el-button-hover-border-color: var(--green-dark);
}

.el-tabs__active-bar {
  background-color: var(--green);
}

.el-tabs__item.is-active {
  color: var(--green);
}

.el-tabs__item:hover {
  color: var(--green);
}

.el-pagination .el-pager li.is-active {
  background-color: var(--green);
}

.el-pagination .el-pager li:hover {
  color: var(--green);
}
</style>
