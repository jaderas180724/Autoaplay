<template>
  <div class="payment-form">
    <el-form :model="form" label-position="top">
      <el-form-item label="Monto a agregar (USD)">
        <el-input-number v-model="form.amount" :min="10" :step="10" />
      </el-form-item>
      
      <el-form-item label="Método de pago">
        <el-radio-group v-model="form.currency">
          <el-radio-button label="BTC">Bitcoin</el-radio-button>
          <el-radio-button label="XMR">Monero</el-radio-button>
          <el-radio-button label="USDT">USDT (TRC20)</el-radio-button>
        </el-radio-group>
      </el-form-item>
      
      <el-form-item>
        <div class="summary">
          <p>Recibirás: <strong>{{ credits.toFixed(0) }} créditos</strong></p>
          <p class="rate">1 crédito = $0.10 USD</p>
        </div>
      </el-form-item>
      
      <el-form-item>
        <el-button type="primary" @click="createPayment" :loading="loading">
          Generar Dirección de Pago
        </el-button>
      </el-form-item>
    </el-form>
    
    <div v-if="paymentData" class="payment-info">
      <el-divider />
      <h4>Envía exactamente {{ paymentData.amount }} {{ form.currency }}</h4>
      <p>a la siguiente dirección:</p>
      <el-input
        v-model="paymentData.address"
        readonly
        class="address-input"
      >
        <template #append>
          <el-button @click="copyAddress">Copiar</el-button>
        </template>
      </el-input>
      <p class="warning">
        El pago se confirmará después de 2 confirmaciones de red.
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useUserStore } from '../store/user'

const emit = defineEmits(['success'])
const userStore = useUserStore()

const form = ref({
  amount: 20,
  currency: 'XMR'
})

const loading = ref(false)
const paymentData = ref(null)

const credits = computed(() => form.value.amount / 0.1)

const createPayment = async () => {
  loading.value = true
  try {
    const response = await axios.post('/api/v1/payments/create', {
      amount: form.value.amount,
      currency: form.value.currency,
      credits: credits.value
    }, {
      headers: { Authorization: `Bearer ${userStore.token}` }
    })
    
    paymentData.value = response.data
    ElMessage.success('Dirección generada')
  } catch (error) {
    ElMessage.error('Error al generar pago')
  } finally {
    loading.value = false
  }
}

const copyAddress = () => {
  navigator.clipboard.writeText(paymentData.value.address)
  ElMessage.success('Dirección copiada')
}
</script>

<style scoped>
.summary {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}
.rate {
  color: #909399;
  font-size: 0.9em;
}
.payment-info {
  margin-top: 20px;
  text-align: center;
}
.address-input {
  margin: 15px 0;
}
.warning {
  color: #e6a23c;
  font-size: 0.85em;
}
</style>