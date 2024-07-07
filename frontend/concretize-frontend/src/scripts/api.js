import axios from 'axios';
export const BASE_URL = `http://localhost:${import.meta.env.VITE_BACKEND_PORT}/`
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

export async function simulate(filename, constraintsStr) {
    try {
        let res = await api.post(`/simulate/${filename}`, {"constraints": constraintsStr});
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