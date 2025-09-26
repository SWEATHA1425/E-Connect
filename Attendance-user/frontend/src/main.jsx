import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter,createBrowserRouter, Outlet, Route, RouterProvider, Routes } from "react-router-dom";
import "./index.css";
import App from "./App";
import Clockin from "./components/Clockin";
import Sidebar from "./components/Sidebar";
import Checkauth from "./Utils/Checkauth";
import Setting from "./components/Setting";
import Clockdashboard from "./components/Clockdashboard";
import Clockin_int from "./components/Clockin_int";
import Leave from "./components/Leave";
import LeaveHistory from "./components/LeaveHistory";
import Leaverequest from "./components/Leaverequest";
import Holidaylist from "./components/Holidayslist";
import Workfromhome from "./components/Workfromhome";
import Remote_details from "./components/Remote_details";
import ToDoList from "./components/todo";
import UserProfile from "./components/UserProfile";
import Timemanagement from "./components/Adminfrontend/Timemanagement";
import Employeelist from "./components/Adminfrontend/Employeelist";
import Leavemanagement from "./components/Adminfrontend/Leavemanagement";
import Leaveapproval from "./components/Adminfrontend/Leave_approval";
import Wfh from "./components/Adminfrontend/Wfh_approval";
import AdminProfile from "./components/Adminfrontend/Adminprofile";
import Leavehistory from "./components/Adminfrontend/Leave_History";
import AddUser from "./components/Adminfrontend/new_employee";
import TaskPage from "./components/Taskpage";
import EmployeeDetails from "./components/EmployeeDetails";
// import TaskAssign from "./components/TaskAssign";
import ViewAssignedTask from "./components/ViewAssignedTask";
import TaskDetailsPage from "./components/TaskDetailsPage";
import LoginPage from "./components/Loginpage";
import Navbar from "./components/Navbar";
import TaskProgress from "./components/TaskProgress";
import AssignTask from './components/AssignTask';
import ProgressDetail from './components/progressDetail';



const DashboardPage = () => (
  <Checkauth>
    <div className="flex h-screen w-full flex-col lg:flex-row">
      <Sidebar />
      {/* <Navbar/> */}
      <div
        id="temp"
        className="h-full w-full overflow-x-hidden flex justify-center items-center"
      >
        <Outlet />
      </div>
    </div>
  </Checkauth>
);

/*const rou = [];
const tempdata = [
  rou.map((item) => {
    return item;
  }),
];*/



const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
  },
  // {path:"Login",
  // element:<LoginPage />
  // },
  {
    path: "/User",
    element: <DashboardPage />,
    children: [
      {
        path: "",
        element: <></>,
      },
      {
        path: "Clockin_int",
        element: <Clockin_int />,
        children: [
          {
            path: "",
            element: <Clockin />,
          },
          {
            path: "Clockdashboard",
            element: <Clockdashboard />,
          },
        ],
      },
      {
        path: "Setting",
        element: <Setting />,
      },
      {
        path: "profile",
        element: <UserProfile />,
      },
      {
        path: "todo",
        element: <ToDoList />
      },
      {
        path: "task",
        element: <TaskPage />,
      },
      {
  path: "task/:taskId",
  element: <TaskDetailsPage />,
},

      {
        path: "Leave",
        element: <Leave />,
      },
      {
        path: "LeaveHistory",
        element: <LeaveHistory />,
      },
      {
        path: "Holidaylist",
        element: <Holidaylist />,
      },
      {
        path: "Workfromhome",
        element: <Workfromhome />,
      },
      {
        path: "Leaverequest",
        element: <Leaverequest />,
      },
      {
        path: "Remote_details",
        element: <Remote_details />,
      },
      {
        path: "LeaveManage",
        element: <Leavemanagement />,
      }
      ,
      {
        path: "newUser",
        element: <AddUser />,
      },
      {
        path: "leaveapproval",
        element: <Leaveapproval />,
      },
      {
        path: "wfh",
        element: <Wfh />,
      },
      {
        path: "history",
        element: <Leavehistory />,
      },
      // {
      //   path:":userid",
      //   element:<TaskAssign />
      // },
      {
        path:"viewtask",
        element:<ViewAssignedTask />
      },
      {
  path: "manager-employee",
  element: <TaskProgress/>,
},
{path:"/User/manager-task-detail/:taskId",
  element:<ProgressDetail role="manager" dashboardRoute="/User/manager-employee" commentLabel="Manager" fileUploadLabel="Manager" />, 
},
      {
  path: "hr-manager",
  element: <TaskProgress/>,
},
{path:"/User/hr-task-detail/:taskId",
  element:<ProgressDetail role="hr" dashboardRoute="/User/hr-manager" commentLabel="HR" fileUploadLabel="HR" />, 
},
{
  path: "employee-task-assign",
  element: <AssignTask assignType="manager-to-employee" />
},
{
  path: "manager-task-assign",
  element: <AssignTask assignType="hr-to-manager" />
}



    ],
  },

  
  {
    path: "/admin",
    element: <DashboardPage />,
    children: [
      {
        path: "",
        element: <></>,
      },
      {
        path: "leave",
        element: <Leavemanagement />,
      },
      {
        path: "time",
        element: <Timemanagement />,
      },
      {
        path: "employee",
        element: <Employeelist />,
        // children:[{
        //   path:':id',
        //   element:<EmployeeDetails/>
        // },],
      },
      {
        path: "leaveapproval",
        element: <Leaveapproval />,
      },
      {
        path: "wfh",
        element: <Wfh />,
      },
      {
        path: "profile",
        element: <AdminProfile />,
      },
      {
        path: "history",
        element: <Leavehistory />,
      },
      {
        path: "newUser",
        element: <AddUser />,
      },
      {
        path:':id',
        element:<EmployeeDetails/>
      }
      
    ],
  },
]);


const MainApp = () => {
  useEffect(() => {
    const handleBeforeUnload = (event) => {
      const isRunning = localStorage.getItem("isRunning") === "true";
      if (isRunning) {
        const confirmationMessage = "Are you sure you want to leave?";
        event.preventDefault();
        event.returnValue = confirmationMessage;
        return confirmationMessage;
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);

    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, []);

  return (
    <RouterProvider router={router}>
      <Outlet />
      <BrowserRouter>
      <Routes>
        <Route path="/admin/employee" element={<Employeelist/>}/>
        <Route path="/admin/employee/:id" element={<EmployeeDetails/>}/>
      </Routes>
      
      </BrowserRouter>
    </RouterProvider>
   

    
  );
};

createRoot(document.getElementById("root")).render(<MainApp />);
