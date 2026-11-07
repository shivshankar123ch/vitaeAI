import axios from 'axios';

export default axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || 'https://vitaeai-tkbp.onrender.com',
    withCredentials: true,
});

// import axios from 'axios';

// export default axios.create({
//     REGISTER_URL: 'https://vitaeai-tkbp.onrender.com/token',
//     headers: {
//         'Content-Type': 'application/json'
//     },
//     withCredentials: true
// });
