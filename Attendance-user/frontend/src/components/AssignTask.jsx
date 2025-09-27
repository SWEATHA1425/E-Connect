import React, { useState, useEffect } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import axios from "axios";
import { ipadr, LS } from "../Utils/Resuse";
import { Modal } from "./Modal";
import { createPortal } from "react-dom";
import Multiselect from 'multiselect-react-dropdown';
import { RotateCw } from "lucide-react";
import { toast } from "react-toastify";
import { parseISO, isWithinInterval } from 'date-fns';
import { AiOutlineDelete, AiOutlineEdit } from 'react-icons/ai';

// Note Component
const Note = ({ empdata, handleDelete, handleEdit }) => (
  <div className={
    `${empdata.bg ? empdata.bg : 'bg-green-300'} p-6 pt-12 w-[320px] min-h-[250px] relative flex flex-col rounded-lg shadow-xl border-l-[10px] border-grey-500 transition-all transform animate-fade-in ` +
    'hover:scale-[1.03] hover:shadow-2xl hover:shadow-green-400/40 hover:z-20 hover:-translate-y-2 cursor-pointer'
  }>
    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-24 h-6 bg-gray-400 opacity-30 rounded-b-lg"></div>
    <p className="text-gray-900 font-bold text-xl mb-3 text-center">📝 Task Details</p>
    <ul className="text-gray-800 text-base space-y-2">
      <li><span className="font-semibold">Task:</span>  <p className="break-words whitespace-normal">{empdata.task}</p></li>
      <li><span className="font-semibold">Assigned Date:</span> {empdata.date}</li>
  <li><span className="font-semibold">Due Date:</span> {empdata.due_date ? String(empdata.due_date).slice(0, 10) : ''}</li>
      <li>
        <span className="font-semibold">Status:</span>
        <span className={`ml-2 px-3 py-1 text-xs font-bold rounded-full shadow-md ${empdata.status === 'Completed' ? 'bg-green-500 text-white' : empdata.status === 'Pending' ? 'bg-yellow-500 text-black' : 'bg-red-500 text-white'}`}>{empdata.status}</span>
      </li>
      <li>
        <span className="font-semibold">Assigned By:</span> {empdata.assigned_by}
      </li>
      <li>
        <span className="font-semibold">Priority:</span>
        <span className={`ml-2 px-3 py-1 text-xs font-bold rounded-full shadow-md ${empdata.priority === "High" ? "bg-red-500 text-white" : empdata.priority === "Medium" ? "bg-yellow-400 text-black" : "bg-green-400 text-black"}`}>{empdata.priority}</span>
      </li>
      {empdata.subtasks && empdata.subtasks.map((subtask, idx) => {
        const text = subtask.text ?? subtask.title ?? "";
        const completed = subtask.completed || false;
        const subtaskKey = `subtask-${empdata._id || empdata.id || empdata.taskid}-${idx}`;
        return (
          <div key={subtaskKey} className="flex items-center text-sm">
            <span className={`mr-2 ${completed ? 'text-green-500' : 'text-gray-400'}`}>{completed ? '✓' : '○'}</span>
            <span className={completed ? 'line-through text-gray-500' : '' + ' break-words whitespace-normal'} style={{wordBreak: 'break-word', overflowWrap: 'break-word', maxWidth: '220px'}}>{text}</span>
          </div>
        );
      })}
    </ul>
    <div className="absolute top-2 right-4 flex gap-2">
      <button className="bg-green-600 text-white p-2 rounded-full shadow-lg transition-transform transform hover:scale-110 hover:-rotate-6 hover:shadow-green-500" onClick={() => handleEdit(empdata.taskid || empdata._id || empdata.id)}>
        <AiOutlineEdit className="text-xl" />
      </button>
      <button className="bg-red-600 text-white p-2 rounded-full shadow-lg transition-transform transform hover:scale-110 hover:-rotate-6 hover:shadow-red-500" onClick={() => handleDelete(empdata.taskid || empdata._id || empdata.id)}>
        <AiOutlineDelete className="text-xl" />
      </button>
    </div>
  </div>
);

const AssignTask = ({ assignType }) => {
  // assignType: 'manager-to-employee' or 'hr-to-manager'
  const navigate = useNavigate();
  const params = useParams();
  const [searchParams] = useSearchParams();
  const [employeeData, setEmployeeData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(5);
  const [modalOpen, setModalOpen] = useState(false);
  const [editModel, SetEditmodel] = useState([]);
  const [modeldata, setModelData] = useState({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] });
  const [options, SetOptions] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [ValueSelected, SetValueSelected] = useState('');
  const [dateRange, setDateRange] = useState([{ startDate: null, endDate: null, key: "selection" }]);
  const [showDatePicker, setShowDatePicker] = useState(false);

  // Determine role and API endpoints
  const isManager = assignType === 'manager-to-employee';
  const isHR = assignType === 'hr-to-manager';
  // Filter tasks by dropdown selection
  useEffect(() => {
    if (!ValueSelected) {
      setFilteredData(employeeData);
      return;
    }
    // Find the selected user object
    const selectedUser = options.find(opt => String(opt.userid) === String(ValueSelected));
    if (!selectedUser) {
      setFilteredData(employeeData);
      return;
    }
    // Filter tasks where assigned_to, assigned_to_name, or userid matches
    const filtered = employeeData.filter((task) => {
      // Some APIs may use assigned_to, assigned_to_name, or userid
      if (Array.isArray(task.assigned_to)) {
        if (task.assigned_to.includes(selectedUser.name) || task.assigned_to.includes(selectedUser.userid)) return true;
      }
      if (task.assigned_to && (task.assigned_to === selectedUser.name || task.assigned_to === selectedUser.userid)) return true;
      if (task.assigned_to_name && (task.assigned_to_name === selectedUser.name || task.assigned_to_name === selectedUser.userid)) return true;
      if (task.userid && String(task.userid) === String(selectedUser.userid)) return true;
      return false;
    });
    setFilteredData(filtered);
  }, [ValueSelected, employeeData, options]);

  // Fetch options for dropdown (employees for manager, managers for HR)
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        if (isManager) {
          const res = await axios.get(`${ipadr}/get_team_members?TL=${LS.get('name')}`);
          SetOptions(res.data && Array.isArray(res.data) ? res.data : []);
        } else if (isHR) {
          const res = await axios.get(`${ipadr}/get_manager`);
          SetOptions(res.data ? [res.data] : []);
        }
      } catch {
        SetOptions([]);
      }
    };
    fetchOptions();
  }, [isManager, isHR]);

  // Fetch tasks for the current view
  useEffect(() => {
    fetchTasks();
  }, [assignType]);

  const fetchTasks = async () => {
    setLoading(true);
    setError('');
    try {
      let url = '';
      if (isManager) {
        url = `${ipadr}/get_assigned_task?TL=${LS.get('name')}&manager_id=${LS.get('id')}`;
      } else if (isHR) {
        // HR should fetch all managers and their tasks
        url = `${ipadr}/get_manager`;
        const res = await axios.get(url);
        const managers = Array.isArray(res.data) ? res.data : [res.data];
        let allTasks = [];
        for (const manager of managers) {
          if (!manager.userid) continue;
          const taskRes = await axios.get(`${ipadr}/get_manager_hr_tasks/${manager.userid}`);
          if (Array.isArray(taskRes.data)) {
            allTasks = allTasks.concat(taskRes.data);
          }
        }
        setEmployeeData(allTasks);
        setFilteredData(allTasks);
        setLoading(false);
        return;
      }
      const res = await axios.get(url);
      const data = res.data && Array.isArray(res.data) ? res.data : [];
      setEmployeeData(data);
      setFilteredData(data);
    } catch (err) {
      setEmployeeData([]);
      setFilteredData([]);
      setError("Error while fetching tasks");
    } finally {
      setLoading(false);
    }
  };

  // Handle Add/Edit/Delete
  const handleDelete = async (taskId) => {
    if (!taskId) return toast.error("Invalid task ID");
    try {
      const response = await fetch(`${ipadr}/task_delete/${taskId}`, { method: "DELETE", headers: { "Content-Type": "application/json" } });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Failed to delete task");
      toast.success("Task deleted successfully!");
      fetchTasks();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleEdit = async (id) => {
    try {
      const response = await axios.get(`${ipadr}/get_single_task/${id}`);
      const taskdetails = response.data;
      let actualTaskData = Array.isArray(taskdetails) ? taskdetails[0] : (taskdetails.task || taskdetails);
      // Ensure comments and files are present for later preservation
      SetEditmodel([{ 
        ...actualTaskData, 
        subtasks: normalizeSubtasks(actualTaskData.subtasks || []),
        comments: actualTaskData.comments || [],
        files: actualTaskData.files || []
      }]);
      setModalOpen(true);
    } catch (error) {
      toast.error("Error fetching task details");
    }
  };

  // Normalize subtasks
  const normalizeSubtasks = (subtasks) => (Array.isArray(subtasks) ? subtasks.map((s, idx) => ({ id: s.id || `subtask_${Date.now()}_${idx}_${Math.random()}`, title: s.title || s.text || "", text: s.text || s.title || "", completed: s.completed ?? s.done ?? false, done: s.done ?? s.completed ?? false })) : []);

  // Add/Edit Task
  const handleonSubmit = async () => {
    if (!modeldata.task.some(task => task.trim() !== "")) return toast.error("Task title is required");
    if (!modeldata.due_date) return toast.error("Due date is required");
    if ((isManager || isHR) && selectedUsers.length === 0) return toast.error(isManager ? "Please select an employee" : "Please select a manager");
    let taskArr = [];
  // Always format due_date as yyyy-mm-dd for the input
    const formatDate = (dateStr) => {
      if (!dateStr) return "";
      // If already yyyy-mm-dd, return as is
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
      // If dd-mm-yyyy or dd/mm/yyyy, convert
      const parts = dateStr.split(/[-\/]/);
      if (parts.length === 3 && parts[2].length === 4) {
        // dd-mm-yyyy to yyyy-mm-dd
        return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      return dateStr;
    };
    try {
      for (let i = 0; i < selectedUsers.length; i++) {
        const taskdetails = {
          Tasks: modeldata.task,
          userid: selectedUsers?.[i]?.userid,
          assigned_by: LS.get("name"),
          date: new Date().toISOString().split("T")[0],
        due_date: formatDate(modeldata.due_date),
          priority: modeldata.priority || "Medium",
          subtasks: normalizeSubtasks(modeldata.subtasks || []),
        };
        taskArr.push(taskdetails);
      }
      const response = await axios({ method: "post", url: `${ipadr}/task_assign_to_multiple_members`, data: { Task_details: taskArr }, headers: { "Content-Type": "application/json" } });
      if (response.status === 200) {
        toast.success(isManager ? "Task assigned to employee(s)" : "Task assigned to manager(s)");
        setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] });
        setSelectedUsers([]);
        setModalOpen(false);
        // Ensure fields are cleared after modal closes
        setTimeout(() => {
          setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] });
          setSelectedUsers([]);
        }, 300);
        fetchTasks();
      } else {
        toast.error("Error while adding the task");
      }
    } catch (error) {
      toast.error("Error submitting task");
    }
  };

  // Edit Task Submit
//   const handleoneditSubmit = async () => {
//     try {
//       if (!editModel || editModel.length === 0) return toast.error("No task data to update");
//       const item = editModel[0];
//       const updatedetails = {
//         updated_task: Array.isArray(item.task) ? item.task[0] : item.task,
//         userid: item.userid,
//         status: item.status,
//       due_date: formatDate(item.due_date),
//         priority: item.priority || "Medium",
//         taskid: item._id,
//         subtasks: normalizeSubtasks(item.subtasks || [])
//       };
//       const response = await axios({ method: 'put', url: `${ipadr}/edit_task`, data: updatedetails, headers: { 'Content-Type': 'application/json' } });
//       if (response.status === 200) {
//         toast.success("Task edited successfully");
//         setModalOpen(false);
//         SetEditmodel([]);
//         // Also clear add modal fields to prevent pre-fill
//         setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] });
//         setSelectedUsers([]);
//         fetchTasks();
//       } else {
//         toast.error("Error while editing the task");
//       }
//     } catch (error) {
//       toast.error("Error editing task");
//     }
//   };
const handleoneditSubmit = async () => {
  try {
    if (!editModel || editModel.length === 0) return toast.error("No task data to update");
    const item = editModel[0];

    // Always format due_date as yyyy-mm-dd
    const formatDate = (dateStr) => {
      if (!dateStr) return "";
      if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
      const parts = dateStr.split(/[-\/]/);
      if (parts.length === 3 && parts[2].length === 4) {
        return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
      }
      return dateStr;
    };

    const updatedetails = {
      updated_task: Array.isArray(item.task) ? item.task[0] : item.task,
      userid: item.userid,
      status: item.status,
      due_date: formatDate(item.due_date),
      priority: item.priority || "Medium",
      taskid: item._id,
      subtasks: normalizeSubtasks(item.subtasks || []),
      // Preserve comments and files even if not shown in UI
      comments: item.comments || [],
      files: item.files || []
    };

    const response = await axios({
      method: 'put',
      url: `${ipadr}/edit_task`,
      data: updatedetails,
      headers: { 'Content-Type': 'application/json' }
    });

    if (response.status === 200) {
      toast.success("Task edited successfully");
      setModalOpen(false);
      SetEditmodel([]);
      setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] });
      setSelectedUsers([]);
      fetchTasks();
    } else {
      toast.error("Error while editing the task");
      console.error("Edit task error response:", response);
    }
  } catch (error) {
    toast.error("Error editing task");
  }
};

  // UI
  if (loading) return <div className="flex justify-center items-center h-64 text-xl">Loading tasks...</div>;
  if (error) return <div className="flex justify-center items-center h-64 text-xl text-red-500">Error: {error}</div>;

  return (
    <div className="mr-8 p-10 bg-white min-h-96 lg:min-h-[90vh] w-full shadow-black rounded-xl justify-center items-center relative jsonback ml-10 rounded-md h-screen overflow-y-scroll scrollbar-hide">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-5xl font-semibold font-inter pb-2 text-transparent bg-gradient-to-r from-zinc-600 to-zinc-950 bg-clip-text border-b-2">Task Assign</h1>
        <button onClick={() => navigate(isManager ? '/User/manager-employee' : '/User/hr-manager')} className="px-4 py-2 bg-blue-700 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">← Back to Dashboard</button>
      </div>
      <header className="px-5 py-4 border-b border-gray-200 flex justify-between items-center">
        <button className="bg-blue-500 hover:bg-blue-400 hover:text-slate-900 text-white text-sm font-inter px-4 py-2 rounded-full shadow-lg" onClick={() => setModalOpen(true)}>Add Task</button>
        <div className="flex items-center space-x-3">
          <select className="w-48 border border-gray-400 rounded-lg px-4 py-2 text-gray-700 bg-white shadow-md outline-none focus:ring-2 focus:ring-blue-500 transition" value={ValueSelected} onChange={e => SetValueSelected(e.target.value)}>
            <option value="">--select {isManager ? 'Employee' : 'Manager'}--</option>
            {options.map(item => (
              <option key={item.id || item.userid} value={item.userid}>{item.name}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-4">
          <button onClick={() => { setFilteredData(employeeData); SetValueSelected(''); }} className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 flex items-center gap-2"><RotateCw className="w-4 h-4" />Reset</button>
        </div>
      </header>
      <div className="notes border-t-2 border-gray-200 mt-5 pt-5 container mx-auto grid md:grid-cols-4 gap-10 ">
        {filteredData && filteredData.length > 0 ? (
          filteredData.map((item, i) => (
            <Note handleDelete={() => handleDelete(item._id || item.id || item.taskid)} handleEdit={() => handleEdit(item._id || item.id || item.taskid)} key={item._id || item.id || item.taskid || i} empdata={item} />
          ))
        ) : (
          <div className="col-span-4 text-center py-8">
            <p className="text-gray-500 text-lg">No tasks found. Please add a new task.</p>
          </div>
        )}
      </div>
      {modalOpen && createPortal(
        <Modal closeModal={() => { setModalOpen(false); setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] }); setSelectedUsers([]); }} onSubmit={handleonSubmit} onCancel={() => { setModalOpen(false); setModelData({ task: [""], userid: "", date: "", due_date: "", priority: "Medium", subtasks: [] }); setSelectedUsers([]); }}>
          <div className="max-h-[50vh] overflow-y-auto">
            {modeldata.task.map((task, index) => (
              <div key={index} className="mb-4">
                <label className="block text-lg font-semibold text-gray-700 mb-2">Task {index + 1}</label>
                <textarea name={`task-${index}`} value={task} onChange={e => { const newTasks = [...modeldata.task]; newTasks[index] = e.target.value; setModelData({ ...modeldata, task: newTasks }); }} className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition placeholder-gray-500" placeholder="Enter task description..." />
              </div>
            ))}
            <button type="button" onClick={() => setModelData({ ...modeldata, task: [...modeldata.task, ""] })} className="bg-gradient-to-r from-blue-500 to-purple-500 text-white font-medium px-4 py-2 rounded-lg shadow-md hover:scale-105 transition transform mb-4">➕ Add Another Task</button>
            <div className="mt-4">
              <label className="block text-lg font-semibold text-gray-700 mb-2">Due date</label>
              <input type="date" name="due_date" value={modeldata.due_date ? String(modeldata.due_date).slice(0, 10) : ''} onChange={e => setModelData({ ...modeldata, due_date: e.target.value })} min={new Date().toISOString().split("T")[0]} className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:ring-2 focus:ring-pink-400 focus:border-pink-400 transition cursor-pointer" />
            </div>
            <div className="mt-4">
              <label className="block text-lg font-semibold text-gray-700 mb-2">Priority</label>
              <select name="priority" value={modeldata.priority || ""} onChange={e => setModelData({ ...modeldata, priority: e.target.value })} className="w-full border border-gray-300 rounded-lg px-4 py-3 shadow-sm focus:ring-2 focus:ring-blue-400 focus:border-blue-400">
                <option value="">Select Priority</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
            <div className="mt-4">
              <label className="block text-lg font-semibold text-gray-700 mb-2">Subtasks</label>
              {modeldata.subtasks?.map((subtask, idx) => (
                <div key={idx} className="flex items-center mb-2">
                  <input type="checkbox" checked={subtask.done} onChange={() => { const updated = [...modeldata.subtasks]; updated[idx].done = !updated[idx].done; setModelData({ ...modeldata, subtasks: updated }); }} className="mr-2" />
                  <input type="text" value={subtask.title} onChange={e => { const updated = [...modeldata.subtasks]; updated[idx].title = e.target.value; setModelData({ ...modeldata, subtasks: updated }); }} className="w-full border border-gray-300 rounded px-2 py-1" />
                </div>
              ))}
              <button onClick={() => setModelData({ ...modeldata, subtasks: [...(modeldata.subtasks || []), { title: "", done: false }] })} className="text-blue-500 mt-2">➕ Add Subtask</button>
            </div>
            <div className="mt-4">
              <label className="block text-lg font-semibold text-gray-700 mb-2">Select {isManager ? 'Employee(s)' : 'Manager(s)'}</label>
              <div className="w-full max-w-sm bg-white border border-gray-300 rounded-lg px-4 py-2 shadow-sm">
                <Multiselect options={options} selectedValues={selectedUsers} onSelect={setSelectedUsers} onRemove={setSelectedUsers} displayValue="name" className="text-gray-700" />
              </div>
            </div>
          </div>
        </Modal>, document.body)}
      {modalOpen && editModel.length > 0 && createPortal(
        <Modal closeModal={() => { setModalOpen(false); SetEditmodel([]); }} onSubmit={handleoneditSubmit} onCancel={() => { setModalOpen(false); SetEditmodel([]); }}>
          {editModel.map((item, index) => {
            // Always format due_date as yyyy-mm-dd for the input
            const formatDate = (dateStr) => {
              if (!dateStr) return "";
              if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) return dateStr;
              const parts = dateStr.split(/[-\/]/);
              if (parts.length === 3 && parts[2].length === 4) {
                return `${parts[2]}-${parts[1].padStart(2, '0')}-${parts[0].padStart(2, '0')}`;
              }
              return dateStr;
            };
            return (
              <div key={index} className="space-y-4 max-h-[60vh] overflow-y-auto">
                <div>
                  <label className="block mb-1 font-semibold">Task</label>
                  <textarea name="task" value={Array.isArray(item.task) ? item.task[0] : item.task || ""} onChange={e => { const updated = [...editModel]; updated[index].task = e.target.value; SetEditmodel(updated); }} className="w-full border border-gray-300 rounded px-3 py-2" rows="3" required placeholder="Enter task description..." />
                </div>
                <div>
                  <label className="block mb-1 font-semibold">Due Date</label>
                  <input type="date" name="due_date" value={formatDate(item.due_date)} onChange={e => { const updated = [...editModel]; updated[index].due_date = e.target.value; SetEditmodel(updated); }} required className="w-full border border-gray-300 rounded px-3 py-2" />
                </div>
              <div>
                <label className="block mb-1 font-semibold">Status</label>
                <select name="status" value={item.status || "Not Started"} onChange={e => { const updated = [...editModel]; updated[index].status = e.target.value; SetEditmodel(updated); }} className="w-full border border-gray-300 rounded px-3 py-2">
                  <option value="Not Started">Not Started</option>
                  <option value="In Progress">In Progress</option>
                  <option value="Completed">Completed</option>
                </select>
              </div>
              <div>
                <label className="block mb-1 font-semibold">Priority</label>
                <select name="priority" value={item.priority || "Medium"} onChange={e => { const updated = [...editModel]; updated[index].priority = e.target.value; SetEditmodel(updated); }} className="w-full border border-gray-300 rounded px-3 py-2">
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                </select>
              </div>
              <div>
                <label className="block mb-1 font-semibold">Subtasks</label>
                {(item.subtasks && Array.isArray(item.subtasks) && item.subtasks.length > 0) ? item.subtasks.map((subtask, sidx) => {
                  const text = subtask.text ?? subtask.title ?? "";
                  const completed = subtask.completed ?? subtask.done ?? false;
                  return (
                    <div key={subtask.id || `subtask-${sidx}`} className="flex items-center mb-2 bg-gray-50 p-2 rounded">
                      <input type="checkbox" checked={completed} onChange={e => { const updated = [...editModel]; updated[index].subtasks[sidx].completed = e.target.checked; SetEditmodel(updated); }} className="mr-2" />
                      <input type="text" value={text} onChange={e => { const updated = [...editModel]; updated[index].subtasks[sidx].text = e.target.value; SetEditmodel(updated); }} className="flex-1 border border-gray-300 rounded px-2 py-1" placeholder="Enter subtask description..." />
                      <button type="button" onClick={() => { const updated = [...editModel]; updated[index].subtasks = updated[index].subtasks.filter((_, i) => i !== sidx); SetEditmodel(updated); }} className="ml-2 px-2 py-1 text-red-500 hover:text-red-700 hover:bg-red-100 rounded">✕</button>
                    </div>
                  );
                }) : <div className="text-gray-500 italic mb-2">No subtasks found</div>}
                <button type="button" onClick={() => { const updated = [...editModel]; if (!updated[index].subtasks) updated[index].subtasks = []; updated[index].subtasks.push({ id: `subtask_${Date.now()}_${Math.random()}`, text: "", title: "", completed: false, done: false }); SetEditmodel(updated); }} className="w-full mt-2 py-2 px-4 bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors">+ Add Subtask</button>
              </div>
            </div>
            );
          })}
        </Modal>, document.body)}
    </div>
  );
};

export default AssignTask;
