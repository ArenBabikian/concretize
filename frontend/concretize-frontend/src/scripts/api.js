import axios from 'axios';
const api = axios.create({
    baseURL: 'http://localhost:5000/'
});

export async function generate(constraints, args) {
    let res = await api.post("/generate", {"constraints": constraints, "args": args});
    return res;
}