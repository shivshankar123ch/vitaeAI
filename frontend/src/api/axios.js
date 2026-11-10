import axios from 'axios';

export default axios.create({
    baseURL: process.env.REACT_APP_API_BASE_URL || 'https://vitae-9hvk.onrender.com',
    withCredentials: true,
});

// import axios from 'axios';

// export default axios.create({
//     REGISTER_URL: 'https://vitae-9hvk.onrender.com/token',
//     headers: {
//         'Content-Type': 'application/json'
//     },
//     withCredentials: true
// });
