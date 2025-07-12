<template>
  <DashboardLayout>
    <div class="container-fluid px-4">
      <!-- Page Header -->
      <div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom">
        <h1 class="h2">
          <i class="fas fa-cog me-2"></i>
          Settings
        </h1>
        <div class="btn-toolbar mb-2 mb-md-0">
          <div class="btn-group me-2">
            <button type="button" class="btn btn-sm btn-success" @click="saveSettings">
              <i class="fas fa-save me-1"></i>
              Save Changes
            </button>
          </div>
        </div>
      </div>

      <div class="row">
        <!-- Settings Navigation -->
        <div class="col-md-3">
          <div class="list-group">
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'account' }"
              @click="activeTab = 'account'"
            >
              <i class="fas fa-user me-2"></i>
              Account Settings
            </a>
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'security' }"
              @click="activeTab = 'security'"
            >
              <i class="fas fa-shield-alt me-2"></i>
              Security
            </a>
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'notifications' }"
              @click="activeTab = 'notifications'"
            >
              <i class="fas fa-bell me-2"></i>
              Notifications
            </a>
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'privacy' }"
              @click="activeTab = 'privacy'"
            >
              <i class="fas fa-eye me-2"></i>
              Privacy
            </a>
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'display' }"
              @click="activeTab = 'display'"
            >
              <i class="fas fa-palette me-2"></i>
              Display
            </a>
            <a
              href="#"
              class="list-group-item list-group-item-action"
              :class="{ active: activeTab === 'data' }"
              @click="activeTab = 'data'"
            >
              <i class="fas fa-database me-2"></i>
              Data & Export
            </a>
          </div>
        </div>

        <!-- Settings Content -->
        <div class="col-md-9">
          <!-- Account Settings -->
          <div v-if="activeTab === 'account'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-user me-2"></i>
                Account Settings
              </h5>
            </div>
            <div class="card-body">
              <form>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="displayName" class="form-label">Display Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="displayName"
                      v-model="settings.account.displayName"
                    />
                  </div>
                  <div class="col-md-6">
                    <label for="username" class="form-label">Username</label>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="settings.account.username"
                    />
                  </div>
                </div>
                <div class="mb-3">
                  <label for="language" class="form-label">Language</label>
                  <select class="form-select" id="language" v-model="settings.account.language">
                    <option value="en">English</option>
                    <option value="es">Spanish</option>
                    <option value="fr">French</option>
                    <option value="de">German</option>
                    <option value="it">Italian</option>
                  </select>
                </div>
                <div class="mb-3">
                  <label for="timezone" class="form-label">Timezone</label>
                  <select class="form-select" id="timezone" v-model="settings.account.timezone">
                    <option value="EST">Eastern Standard Time</option>
                    <option value="CST">Central Standard Time</option>
                    <option value="MST">Mountain Standard Time</option>
                    <option value="PST">Pacific Standard Time</option>
                    <option value="GMT">Greenwich Mean Time</option>
                  </select>
                </div>
                <div class="form-check">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="publicProfile"
                    v-model="settings.account.publicProfile"
                  />
                  <label class="form-check-label" for="publicProfile">
                    Make my profile public
                  </label>
                </div>
              </form>
            </div>
          </div>

          <!-- Security Settings -->
          <div v-if="activeTab === 'security'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-shield-alt me-2"></i>
                Security Settings
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>Password</h6>
                <p class="text-muted">Last changed 3 months ago</p>
                <button class="btn btn-outline-primary">Change Password</button>
              </div>
              
              <div class="mb-4">
                <h6>Two-Factor Authentication</h6>
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="twoFactorAuth"
                    v-model="settings.security.twoFactorAuth"
                  />
                  <label class="form-check-label" for="twoFactorAuth">
                    Enable two-factor authentication
                  </label>
                </div>
                <p class="text-muted mt-2">Add an extra layer of security to your account</p>
              </div>

              <div class="mb-4">
                <h6>Login Notifications</h6>
                <div class="form-check form-switch">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="loginNotifications"
                    v-model="settings.security.loginNotifications"
                  />
                  <label class="form-check-label" for="loginNotifications">
                    Notify me of new login attempts
                  </label>
                </div>
              </div>

              <div class="mb-4">
                <h6>Active Sessions</h6>
                <div class="card">
                  <div class="card-body">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                      <div>
                        <strong>Current Session</strong>
                        <br />
                        <small class="text-muted">Chrome on Linux - Current location</small>
                      </div>
                      <span class="badge bg-success">Active</span>
                    </div>
                    <button class="btn btn-sm btn-outline-danger">End All Other Sessions</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Notifications Settings -->
          <div v-if="activeTab === 'notifications'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-bell me-2"></i>
                Notification Preferences
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>Email Notifications</h6>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="emailCollection"
                    v-model="settings.notifications.email.newItems"
                  />
                  <label class="form-check-label" for="emailCollection">
                    New items added to collections
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="emailDealer"
                    v-model="settings.notifications.email.dealerUpdates"
                  />
                  <label class="form-check-label" for="emailDealer">
                    Dealer updates and offers
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="emailWeekly"
                    v-model="settings.notifications.email.weeklyDigest"
                  />
                  <label class="form-check-label" for="emailWeekly">
                    Weekly summary digest
                  </label>
                </div>
              </div>

              <div class="mb-4">
                <h6>Browser Notifications</h6>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="browserAlerts"
                    v-model="settings.notifications.browser.alerts"
                  />
                  <label class="form-check-label" for="browserAlerts">
                    Show browser notifications
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="browserReminders"
                    v-model="settings.notifications.browser.reminders"
                  />
                  <label class="form-check-label" for="browserReminders">
                    Collection update reminders
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Privacy Settings -->
          <div v-if="activeTab === 'privacy'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-eye me-2"></i>
                Privacy Settings
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>Profile Visibility</h6>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="profileVisibility"
                    id="profilePublic"
                    value="public"
                    v-model="settings.privacy.profileVisibility"
                  />
                  <label class="form-check-label" for="profilePublic">
                    Public - Anyone can see my profile and collections
                  </label>
                </div>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="profileVisibility"
                    id="profileFriends"
                    value="friends"
                    v-model="settings.privacy.profileVisibility"
                  />
                  <label class="form-check-label" for="profileFriends">
                    Friends only - Only connected users can see my profile
                  </label>
                </div>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="profileVisibility"
                    id="profilePrivate"
                    value="private"
                    v-model="settings.privacy.profileVisibility"
                  />
                  <label class="form-check-label" for="profilePrivate">
                    Private - Keep my profile completely private
                  </label>
                </div>
              </div>

              <div class="mb-4">
                <h6>Data Sharing</h6>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="shareAnalytics"
                    v-model="settings.privacy.shareAnalytics"
                  />
                  <label class="form-check-label" for="shareAnalytics">
                    Share anonymous usage analytics
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="shareCollectionData"
                    v-model="settings.privacy.shareCollectionData"
                  />
                  <label class="form-check-label" for="shareCollectionData">
                    Allow collection data for market insights
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Display Settings -->
          <div v-if="activeTab === 'display'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-palette me-2"></i>
                Display Preferences
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>Theme</h6>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="theme"
                    id="themeLight"
                    value="light"
                    v-model="settings.display.theme"
                  />
                  <label class="form-check-label" for="themeLight">
                    Light theme
                  </label>
                </div>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="theme"
                    id="themeDark"
                    value="dark"
                    v-model="settings.display.theme"
                  />
                  <label class="form-check-label" for="themeDark">
                    Dark theme
                  </label>
                </div>
                <div class="form-check mb-2">
                  <input
                    class="form-check-input"
                    type="radio"
                    name="theme"
                    id="themeAuto"
                    value="auto"
                    v-model="settings.display.theme"
                  />
                  <label class="form-check-label" for="themeAuto">
                    Auto (follows system setting)
                  </label>
                </div>
              </div>

              <div class="mb-4">
                <h6>Layout Options</h6>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="compactMode"
                    v-model="settings.display.compactMode"
                  />
                  <label class="form-check-label" for="compactMode">
                    Compact mode
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="showTooltips"
                    v-model="settings.display.showTooltips"
                  />
                  <label class="form-check-label" for="showTooltips">
                    Show helpful tooltips
                  </label>
                </div>
              </div>

              <div class="mb-4">
                <h6>Currency Display</h6>
                <select class="form-select" v-model="settings.display.currency">
                  <option value="USD">US Dollar ($)</option>
                  <option value="EUR">Euro (€)</option>
                  <option value="GBP">British Pound (£)</option>
                  <option value="CAD">Canadian Dollar (C$)</option>
                  <option value="AUD">Australian Dollar (A$)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Data & Export Settings -->
          <div v-if="activeTab === 'data'" class="card">
            <div class="card-header">
              <h5 class="mb-0">
                <i class="fas fa-database me-2"></i>
                Data Management
              </h5>
            </div>
            <div class="card-body">
              <div class="mb-4">
                <h6>Export Data</h6>
                <p class="text-muted">Download your collection data in various formats</p>
                <div class="btn-group" role="group">
                  <button type="button" class="btn btn-outline-primary">
                    <i class="fas fa-file-csv me-1"></i>
                    Export as CSV
                  </button>
                  <button type="button" class="btn btn-outline-primary">
                    <i class="fas fa-file-excel me-1"></i>
                    Export as Excel
                  </button>
                  <button type="button" class="btn btn-outline-primary">
                    <i class="fas fa-file-code me-1"></i>
                    Export as JSON
                  </button>
                </div>
              </div>

              <div class="mb-4">
                <h6>Backup Settings</h6>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="autoBackup"
                    v-model="settings.data.autoBackup"
                  />
                  <label class="form-check-label" for="autoBackup">
                    Enable automatic backups
                  </label>
                </div>
                <div class="form-check form-switch mb-2">
                  <input
                    class="form-check-input"
                    type="checkbox"
                    id="cloudSync"
                    v-model="settings.data.cloudSync"
                  />
                  <label class="form-check-label" for="cloudSync">
                    Sync data to cloud storage
                  </label>
                </div>
                <button type="button" class="btn btn-outline-success">
                  <i class="fas fa-cloud-download-alt me-1"></i>
                  Create Manual Backup
                </button>
              </div>

              <div class="mb-4">
                <h6 class="text-danger">Danger Zone</h6>
                <div class="card border-danger">
                  <div class="card-body">
                    <h6 class="card-title text-danger">Delete Account</h6>
                    <p class="card-text">
                      Permanently delete your account and all associated data. This action cannot be undone.
                    </p>
                    <button type="button" class="btn btn-danger">
                      <i class="fas fa-trash me-1"></i>
                      Delete Account
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DashboardLayout from '@/components/dashboard/DashboardLayout.vue'

const activeTab = ref('account')

const settings = ref({
  account: {
    displayName: 'John Doe',
    username: 'johndoe',
    language: 'en',
    timezone: 'EST',
    publicProfile: true
  },
  security: {
    twoFactorAuth: false,
    loginNotifications: true
  },
  notifications: {
    email: {
      newItems: true,
      dealerUpdates: true,
      weeklyDigest: false
    },
    browser: {
      alerts: true,
      reminders: false
    }
  },
  privacy: {
    profileVisibility: 'friends',
    shareAnalytics: true,
    shareCollectionData: false
  },
  display: {
    theme: 'light',
    compactMode: false,
    showTooltips: true,
    currency: 'USD'
  },
  data: {
    autoBackup: true,
    cloudSync: false
  }
})

const saveSettings = () => {
  // Mock save functionality
  console.log('Settings saved:', settings.value)
  // Show success message or handle save logic
  alert('Settings saved successfully!')
}
</script>

<style scoped>
.card {
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  border: 1px solid rgba(0, 0, 0, 0.125);
}

.list-group-item {
  cursor: pointer;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}

.list-group-item.active {
  background-color: #007bff;
  border-color: #007bff;
}

.form-check-input:checked {
  background-color: #007bff;
  border-color: #007bff;
}

.border-danger {
  border-color: #dc3545 !important;
}
</style>
