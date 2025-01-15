import { Router, Request, Response } from "express";
import axios from "axios";
import dotenv from "dotenv";
dotenv.config();

const router = Router();
const baseEdnpoint = process.env.FLASK_APP_ENDPOINT
