// 测试环境变量加载
console.log('VITE_API_BASE_URL from process.env:', process.env.VITE_API_BASE_URL)
console.log('所有环境变量:', Object.keys(process.env).filter(key => key.includes('VITE')))

// 检查.env文件内容
import fs from 'fs'
if (fs.existsSync('.env')) {
  const envContent = fs.readFileSync('.env', 'utf8')
  console.log('.env文件内容:', envContent)
}