<template>
  <div class="settings">
    <section class="stats-band">
      <article class="stat">
        <label>发布时间</label>
        <strong>08:00</strong>
        <small>每日定时</small>
      </article>
      <article class="stat">
        <label>图片尺寸</label>
        <strong>1080²</strong>
        <small>像素</small>
      </article>
      <article class="stat">
        <label>Logo 比例</label>
        <strong>13%</strong>
        <small>画面占比</small>
      </article>
      <article class="stat">
        <label>去重天数</label>
        <strong>30</strong>
        <small>天</small>
      </article>
    </section>

    <div class="settings-content">
      <el-tabs v-model="activeTab">
        <!-- 基本设置 -->
        <el-tab-pane label="基本设置" name="basic">
          <el-form :model="form" label-width="140px" style="max-width: 520px">
            <el-form-item label="发布时间">
              <el-time-picker v-model="form.publishTime" format="HH:mm" placeholder="选择发布时间" />
            </el-form-item>
            <el-form-item label="内容池预警阈值">
              <el-input-number v-model="form.warningThreshold" :min="1" :max="20" />
              <span class="form-tip">当可发布内容少于此数量时发出预警</span>
            </el-form-item>
            <el-form-item label="去重天数">
              <el-input-number v-model="form.dedupDays" :min="7" :max="90" />
              <span class="form-tip">多少天内不重复使用相同文案</span>
            </el-form-item>
            <el-form-item>
              <button class="btn primary" @click="handleSave">保存设置</button>
              <button class="btn" @click="handleReset" style="margin-left: 8px">重置</button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 图片设置 -->
        <el-tab-pane label="图片设置" name="image">
          <el-form :model="imageForm" label-width="140px" style="max-width: 520px">
            <el-form-item label="图片尺寸">
              <el-input-number v-model="imageForm.width" :min="800" :max="2000" />
              <span style="margin: 0 8px">×</span>
              <el-input-number v-model="imageForm.height" :min="800" :max="2000" />
              <span class="form-tip">推荐 1080×1080</span>
            </el-form-item>
            <el-form-item label="Logo 大小比例">
              <el-slider v-model="imageForm.logoSizeRatio" :min="0.05" :max="0.3" :step="0.01"
                :format-tooltip="val => (val * 100).toFixed(0) + '%'" style="width: 200px" />
            </el-form-item>
            <el-form-item label="Logo 边距">
              <el-input-number v-model="imageForm.logoMargin" :min="10" :max="100" />
              <span class="form-tip">像素</span>
            </el-form-item>
            <el-form-item label="亮度阈值">
              <el-slider v-model="imageForm.brightnessThreshold" :min="0" :max="255" style="width: 200px" />
              <span class="form-tip">判断使用原色或反白 Logo</span>
            </el-form-item>
            <el-form-item>
              <button class="btn primary" @click="handleSaveImage">保存设置</button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- API 配置 -->
        <el-tab-pane label="API 配置" name="api">
          <el-alert title="安全提示" type="warning"
            description="API 密钥敏感信息，请在后端 .env 文件中配置环境变量。"
            show-icon :closable="false" style="margin-bottom: 20px; max-width: 520px" />
          <el-form label-width="150px" style="max-width: 520px">
            <el-form-item label="OpenAI API Key"><el-input type="password" placeholder="sk-..." show-password disabled /></el-form-item>
            <el-form-item label="Stability API Key"><el-input type="password" placeholder="sk-..." show-password disabled /></el-form-item>
            <el-form-item label="微博 App Key"><el-input type="password" placeholder="请在后端 .env 配置" show-password disabled /></el-form-item>
            <el-form-item label="微博 Access Token"><el-input type="password" placeholder="请在后端 .env 配置" show-password disabled /></el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 关于 -->
        <el-tab-pane label="关于" name="about">
          <div class="about-section">
            <h2>PUDOW 每日一句</h2>
            <p>版本：v1.0.0-beta</p>
            <p>基于 Vue 3 + Element Plus + FastAPI 开发</p>
            <el-divider />
            <h3>功能特性</h3>
            <ul>
              <li>✅ AI 自动生成配图（DALL-E 3 / Stability AI）</li>
              <li>✅ 智能 Logo 水印添加</li>
              <li>✅ 30 天文案去重机制</li>
              <li>✅ 人工审核流程</li>
              <li>✅ 定时自动发布</li>
              <li>✅ 完整的发布日志</li>
            </ul>
            <el-divider />
            <p class="copyright">© 2025 PUDOW 朴道健康水专家</p>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('basic')

const form = reactive({
  publishTime: new Date(2000, 0, 1, 8, 0),
  warningThreshold: 5,
  dedupDays: 30
})

const imageForm = reactive({
  width: 1080, height: 1080,
  logoSizeRatio: 0.13,
  logoMargin: 20,
  brightnessThreshold: 128
})

function handleSave() {
  ElMessage.success('设置已保存（功能开发中）')
}

function handleReset() {
  form.publishTime = new Date(2000, 0, 1, 8, 0)
  form.warningThreshold = 5
  form.dedupDays = 30
  ElMessage.info('已重置为默认值')
}

function handleSaveImage() {
  ElMessage.success('设置已保存（功能开发中）')
}
</script>

<style scoped>
.settings {
  min-height: 100%;
}

.stats-band {
  padding: 18px 28px;
  display: grid;
  grid-template-columns: repeat(4, minmax(150px, 1fr));
  gap: 14px;
  border-bottom: 1px solid var(--line);
  background: #fbfcfb;
}

.stat {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 16px;
  display: grid;
  align-content: space-between;
}

.stat label {
  color: var(--muted);
  font-size: 13px;
}

.stat strong {
  display: block;
  margin-top: 10px;
  font-size: 30px;
  line-height: 1;
}

.stat small {
  margin-top: 8px;
  color: var(--faint);
  font-size: 12px;
}

.settings-content {
  padding: 18px 28px 28px;
}

.form-tip {
  margin-left: 12px;
  font-size: 13px;
  color: var(--muted);
}

.about-section { max-width: 520px; padding: 20px 0; }
.about-section h2 { font-size: 24px; margin-bottom: 16px; color: var(--green); }
.about-section h3 { font-size: 18px; margin: 16px 0; }
.about-section p { margin: 8px 0; color: var(--text); }
.about-section ul { list-style: none; padding: 0; }
.about-section li { padding: 8px 0; color: var(--text); }
.copyright { margin-top: 32px; text-align: center; color: var(--muted); font-size: 14px; }

@media (max-width: 1180px) {
  .stats-band { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 500px) {
  .stats-band { grid-template-columns: 1fr; }
}
</style>
