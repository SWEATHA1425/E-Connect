// import React from "react";
// import logo from "../assets/logo.png";
// import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
// import { ToastContainer } from "react-toastify";
// import "react-toastify/dist/ReactToastify.css";
// import "./login.css";
// import { useNavigate } from "react-router-dom";
// import { Authdata } from "../Utils/Authprovider";
// import { Apisignin } from "../Api/Loginauth";
// import { jwtDecode } from "jwt-decode";
// import { LS } from "../Utils/Resuse";

// export default function LoginPage() {
//   const navigate = useNavigate();
//   const { SetStatedata } = Authdata();

//   const handleGoogleLogin = async (credentialResponse) => {
//     try {
//       let userDecode = jwtDecode(credentialResponse.credential);
//       const res = await Apisignin({
//         client_name: userDecode.name,
//         email: userDecode.email,
//       });
//       const loggedIn = LS.get("isloggedin");
//       const isAdmin  = LS.get("isadmin");
//       if(loggedIn && isAdmin){
//         navigate("admin/time", {
//           state: { id: res.id, token: res.access_token },
//         });
//       }else if(loggedIn || isAdmin){
//         navigate("User/Clockin_int", {
//           state: { id: res.id, token: res.access_token },
//         });
//       } else{
//         console.log("Invalid request")
//       }
//     } catch (err) {
//       console.log(err);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
//       <div className="bg-white shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
//         <div className="flex flex-col items-center justify-center p-8">
//           <div className="text-center mb-6">
//           <img src={logo} alt="Company Logo" className="h-32 mx-auto" />
//             <h1 className="text-2xl font-bold text-gray-700 mt-4">
//               Welcome to E-Connect
//             </h1>
//           </div>
//           <div className="w-full">
//             <h2 className="text-xl font-semibold text-gray-600 mb-4 text-center">
//               Sign in with Google
//             </h2>
//             <div className="flex justify-center">
//               <GoogleOAuthProvider clientId="34401210977-cvn09uafi0cn0pcd7lv9u4t0anjeg8qb.apps.googleusercontent.com">
//                 <GoogleLogin
//                   onSuccess={handleGoogleLogin}
//                   useOneTap
//                 />
//               </GoogleOAuthProvider>
//             </div>
//           </div>
//         </div>
//       </div>

//       <ToastContainer
//         position="bottom-center"
//         autoClose={2000}
//         hideProgressBar={false}
//         newestOnTop={false}
//         closeOnClick
//         rtl={false}
//         pauseOnFocusLoss
//         draggable
//         pauseOnHover
//       />
//     </div>
//   );
// }

import React from 'react';
import logo from '../assets/logo.png';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './login.css';
import { useNavigate } from 'react-router-dom';
import { Authdata } from '../Utils/Authprovider';
import { Apisignin } from '../Api/Loginauth';
import { jwtDecode } from 'jwt-decode';
import { LS, ipadr } from '../Utils/Resuse';

export default function LoginPage() {
  const navigate = useNavigate();
  const { SetStatedata } = Authdata();

  const getIpInfo = async () => {
    try {
      console.log('Attempting to reach:', `${ipadr}/ip-info`);

      const response = await fetch(`${ipadr}/ip-info`, {
        method: 'GET',
        redirect: 'follow',
        // Adding these options might help with certificate issues
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Current IP Information:', {
        publicIp: result.public_ip,
        localIp: result.local_ip,
      });

      return {
        publicIp: result.public_ip,
        localIp: result.local_ip,
      };
    } catch (error) {
      console.error('Error fetching IP info:', error);
      return null;
    }
  };
  const validateIp = (userIp, currentIps) => {
    if (!userIp) {
      console.log('No IP validation needed - IP not present in response');
      return true;
    }

    console.log('Performing IP validation:');
    console.log('User IP from response:', userIp);
    console.log('Current Public IP:', currentIps.publicIp);
    console.log('Current Local IP:', currentIps.localIp);

    const matchesPublic = currentIps.publicIp === userIp;
    const matchesLocal = currentIps.localIp === userIp;

    console.log('Matches public IP:', matchesPublic);
    console.log('Matches local IP:', matchesLocal);

    return matchesPublic || matchesLocal;
  };

  const handleGoogleLogin = async (credentialResponse) => {
    try {
      console.log('Starting Google login process...');

      // First get the current IP information
      const currentIps = await getIpInfo();
      console.log('Retrieved current IPs:', currentIps);

      // Proceed with Google sign-in
      let userDecode = jwtDecode(credentialResponse.credential);
      console.log('Google credentials decoded:', {
        name: userDecode.name,
        email: userDecode.email,
      });

      const res = await Apisignin({
        client_name: userDecode.name,
        email: userDecode.email,
      });
      console.log('API signin response:', res);

      // Check if IP validation is needed
      if (res.ip) {
        console.log('IP validation required. Response IP:', res.ip);

        if (!validateIp(res.ip, currentIps)) {
          console.log('IP validation failed!');
          toast.error(
            'Remote work IP is mismatched. Please connect from an authorized network.'
          );
          return;
        }
        console.log('IP validation successful!');
      } else {
        console.log('No IP validation required');
      }

      // If IP validation passes or is not needed, proceed with navigation
      const loggedIn = LS.get('isloggedin');
      const isAdmin = LS.get('isadmin');

      console.log('Navigation check:', {
        isLoggedIn: loggedIn,
        isAdmin: isAdmin,
      });

      if (loggedIn && isAdmin) {
        console.log('Navigating to admin/time');
        navigate('admin/time', {
          state: { id: res.id, token: res.access_token },
        });
      } else if (loggedIn || isAdmin) {
        console.log('Navigating to User/Clockin_int');
        navigate('User/Clockin_int', {
          state: { id: res.id, token: res.access_token },
        });
      } else {
        console.log('Invalid request - no valid navigation state');
      }
    } catch (err) {
      console.error('Login error:', err);
      toast.error('An error occurred during login. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white shadow-lg rounded-lg overflow-hidden w-full max-w-lg">
        <div className="flex flex-col items-center justify-center p-8">
          <div className="text-center mb-6">
            <img src={logo} alt="Company Logo" className="h-32 mx-auto" />
            <h1 className="text-2xl font-bold text-gray-700 mt-4">
              Welcome to E-Connect
            </h1>
          </div>
          <div className="w-full">
            <h2 className="text-xl font-semibold text-gray-600 mb-4 text-center">
              Sign in with Google
            </h2>
            <div className="flex justify-center">
              <GoogleOAuthProvider clientId="883508437996-0s4hakmhun5ejdtt9ahitverl8eubost.apps.googleusercontent.com">
                <GoogleLogin onSuccess={handleGoogleLogin} useOneTap />
              </GoogleOAuthProvider>
            </div>
          </div>
        </div>
      </div>

      <ToastContainer
        position="bottom-center"
        autoClose={2000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
      />
    </div>
  );
}
