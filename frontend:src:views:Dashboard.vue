<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Mis Créditos</span>
            </div>
          </template>
          <div class="credit-display">
            <h2>${{ userStore.credits.toFixed(2) }}</h2>
            <el-button type="primary" @click="showDeposit = true">
              Agregar Fondos
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Nuevo Check</span>
            </div>
          </template>
          
          <el-form :model="checkForm" label-position="top">
            <el-form-item label="Servicio">
              <el-select v-model="checkForm.service" placeholder="Seleccionar">
                <el-option label="Netflix" value="netflix" />
                <el-option label="Spotify" value="spotify" />
                <el-option label="Crunchyroll" value="crunchyroll" />
                <el-option label="Disney+" value="disney" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="Combos (email:password)">
              <el-input
                v-model="checkForm.combos"
                type="textarea"
                :rows="10"
                placeholder="user1@email.com:password123&#10;user2@email.com:pass456"
              />
            </el-form-item>
            
            <el-form-item>
              <div class="check-info">
                <span>Checks: {{ comboCount }} | Costo: ${{ (comboCount * 0.1).toFixed(2) }}</span>
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="success" 
                @click="startCheck"
                :loading="checking"
                :disabled="comboCount === 0 || userStore.credits < comboCount * 0.1"
              >
                Iniciar Verificación
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Resultados -->
    <el-row v-if="results.length > 0" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Resultados</span>
              <el-button type="primary" size="small" @click="downloadValid">
                Descargar Válidas
              </el-button>
            </div>
          </template>
          
          <el-table :data="results" style="width: 100%">
            <el-table-column prop="email" label="Email" />
            <el-table-column prop="status" label="Estado">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="capture" label="Info" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- Modal Depósito -->
    <el-dialog v-model="showDeposit" title="Agregar Fondos" width="500px">
      <PaymentForm @success="showDeposit = false" />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import PaymentForm from '../components/PaymentForm.vue'

const userStore = useUserStore()
const checking = ref(false)
const showDeposit = ref(false)
const results = ref([])

const checkForm = ref({
  service: 'netflix',
  combos: ''
})

const comboCount = computed(() => {
  return checkForm.value.combos.split('\n').filter(l => l.trim() && l.includes(':')).length
})

const getStatusType = (status) => {
  const types = {
    'valid': 'success',
    'invalid': 'danger',
    'checking': 'warning',
    'error': 'info'
  }
  return types[status] || 'info'
}

const startCheck = async () => {
  checking.value = true
  results.value = []
  
  try {
    const combos = checkForm.value.combos
      .split('\n')
      .filter(l => l.trim() && l.includes(':'))
    
    const response = await axios.post('/api/v1/checks/check', {
      service: checkForm.value.service,
      combos: combos
    }, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    
    results.value = response.data.results
    userStore.fetchCredits() // Actualizar créditos
    
    ElMessage.success('Verificación completada')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Error en verificación')
  } finally {
    checking.value = false
  }
}

const downloadValid = () => {
  const valid = results.value.filter(r => r.status === 'valid')
  const text = valid.map(v => `${v.email}:${v.password}`).join('\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `valid_${checkForm.value.service}.txt`
  a.click()
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}
.credit-display {
  text-align: center;
}
.credit-display h2 {
  font-size: 3em;
  margin: 20px 0;
  color: #67c23a;
}
.check-info {
  color: #666;
  font-size: 0.9em;
}
</style>