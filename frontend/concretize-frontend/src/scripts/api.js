import axios from 'axios';
export const BASE_URL = 'http://localhost:5000/'
const api = axios.create({
    baseURL: BASE_URL
});

export async function generate(constraints, args) {
    let res = await api.post("/generate", {"constraints": constraints, "args": args});
    return res;
}

export async function download(filename) {
    let res = await api.get(`/downloads/${filename}`);
    return res;
}
