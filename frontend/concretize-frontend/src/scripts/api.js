import axios from 'axios';
export const BASE_URL = 'http://localhost:5001/'
const api = axios.create({
    baseURL: BASE_URL
});

export async function generate(constraints, args) {
    try {
        let res = await api.post("/generate", {"constraints": constraints, "args": args});
        return res;
    } catch (e) {
        const resObj = {
            data: {
                error: `API request failed with error ${e.message}`
            }
        }
        return resObj;
    }
}

export async function simulate(filename) {
    try {
        let res = await api.get(`/simulate/${filename}`);
        return res;
    } catch (e) {
        const resObj = {
            data: {
                error: `API request failed with error ${e.message}`
            }
        }
        return resObj;
    }
}