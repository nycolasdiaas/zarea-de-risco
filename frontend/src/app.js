import express  from 'express';
import backend_router from './routes/dataRoutes.js';
import dotenv from "dotenv"
dotenv.config()

const app = express()
const PORT = process.env.API_PORT

app.use(express.json())
app.use('/', backend_router)

app.listen(3003, () => {
  console.log(`Node API rodando na porta: ${PORT}`);
});