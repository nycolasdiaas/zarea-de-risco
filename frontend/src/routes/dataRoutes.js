import Router from "express"
import axios from "axios"
import dotenv from "dotenv"
dotenv.config()

const router = Router()
const baseEdnpoint = process.env.FLASK_APP_ENDPOINT
// const baseEdnpoint = "http://localhost:5000"

router.get("/", async (_, res) => {
    return res.send("API is running.");
  });

router.get("/get_daily_metadata", async (_, res) =>{
    try {
        const response = await axios.get(baseEdnpoint + "/get_daily_metadata")
        console.log(response.data)
    } catch (error){
        console.error(error)
        return res.status(500).json({ error: "Ocorreu um erro ao solicitar metadados." })
    }
})

router.get("/get_metadata_from_date/:date", async (req, res) =>{
    try {
        const date = req.params.date

        const response = await axios.get(baseEdnpoint + "/get_metadata_from_date/" + date)
        console.log("Data retrieved")
        return res.json({ data: response.data } ).status(200)
    } catch (error){
        console.error(error)
        return res.status(500).json({ error: "Ocorreu um erro ao solicitar metadados." })
    }
})

export default router
