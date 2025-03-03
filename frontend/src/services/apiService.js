import axios from "axios"
import dotenv from "dotenv"
dotenv.config()


class ApiService {
  constructor(baseUrl) {
    this.baseUrl = baseUrl
  }

  async getDailyMetadata() {
    try {
      const response = await axios.get(this.baseUrl + "/metadata/daily")
      console.log("Data retrieved.")
      return response
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  async getMetadataFromDate(date) {
    try {
      const response = await axios.get(this.baseUrl + "/metadata/date/" + date)
      console.log("Data retrieved.")
      return response
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  async getMonthlyMetadata() {
    try {
      const response = await axios.get(this.baseUrl + "/metadata/monthly/")
      console.log("Data retrieved.")
      return response
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  async getLastSevenDays() {
    try {
      const response = await axios.get(this.baseUrl + "/metadata/weekly")
      console.log("Data retrieved.")
      return response
    } catch (error) {
      console.error(error)
      throw error
    }
  }

  async getDataFromLocation(state, city, neigborhood, street) {
    try {
      const response = await axios.get(
        this.baseUrl + "/metadata/location/" + `${state}/${city}/${neigborhood}/${street}`
      )
      console.log("Data retrieved.")
      return response
    } catch (error) {
      console.error(error)
      throw error
    }
  }

}


const apiService = new ApiService(process.env.FLASK_APP_ENDPOINT)

export default apiService
