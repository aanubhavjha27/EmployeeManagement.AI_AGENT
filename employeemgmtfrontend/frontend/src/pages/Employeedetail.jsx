import axios from 'axios'
import { X, Pen, Trash } from 'lucide-react'
import React, { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

const Employeedetail = ({ employeeid, setshowemployeedetail, setemployees }) => {
  const [employee, setemployee] = useState(null)
  const [loading, setloading] = useState(true)
  const [edit, setedit] = useState(false)

  useEffect(() => {
    const fetchemployee = async () => {
      try {
        const res = await axios.get(`http://localhost:8080/api/employee/${employeeid}`)
        setemployee(res.data)
      } catch (error) {
        toast.error('Something went wrong')
      } finally {
        setloading(false)
      }
    }
    fetchemployee()
  }, [employeeid])

  const deleteemployeedetail = async () => {
    if (!window.confirm("Delete this employee?")) return

    try {
      await axios.delete(`http://localhost:8080/api/deleteemployee/${employeeid}`)
      setemployees(prev => prev.filter(emp => emp.id !== employeeid))
      toast.success("Employee deleted")
      setshowemployeedetail(false)
    } catch (error) {
      toast.error("Delete failed")
    }
  }

  const saveeditemployee = async () => {
    if (!window.confirm("Save changes?")) return

    try {
      const response = await axios.put(
        `http://localhost:8080/api/updateemployee/${employeeid}`,
        employee
      )

      setemployees(prev =>
        prev.map(emp => (emp.id === employeeid ? response.data : emp))
      )

      toast.success("Updated successfully")
      setshowemployeedetail(false)
    } catch (error) {
      toast.error("Update failed")
    }
  }

  const handleChange = (field) => (e) => {
    setemployee({ ...employee, [field]: e.target.value })
  }

  if (loading) return <div className="fixed inset-0 flex items-center justify-center text-white">Loading...</div>
  if (!employee) return null

 return (
  <div className="h-full w-full flex flex-col text-white bg-gradient-to-br from-slate-900 to-slate-800">

    {/* Header */}
    <div className="flex items-center p-4 border-b border-white/10">
      <h2 className="text-lg font-semibold">Employee Details</h2>

      <div className="ml-auto flex gap-4 items-center">
        <Trash 
          onClick={deleteemployeedetail} 
          className="cursor-pointer hover:text-red-400" 
        />
        <X 
          onClick={() => setshowemployeedetail(false)} 
          className="cursor-pointer hover:text-gray-300" 
        />
      </div>
    </div>

    {/* Body */}
    <div className="flex-1 overflow-y-auto p-4 space-y-3">
      {Object.keys(employee).map((key) => (
        key !== 'id' && (
          <div key={key}>
            <label className="text-sm text-gray-400 capitalize">{key}</label>
            <input
              type={key === 'age' || key === 'salary' ? 'number' : 'text'}
              value={employee[key] ?? ''}
              disabled={!edit}
              onChange={handleChange(key)}
              className={`w-full mt-1 p-2 rounded-lg bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500 ${!edit && 'opacity-70 cursor-not-allowed'}`}
            />
          </div>
        )
      ))}
    </div>

    {/* Footer */}
    <div className="p-4 border-t border-white/10 flex justify-between items-center">
      <button
        onClick={() => setedit(!edit)}
        className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300"
      >
        <Pen size={16} /> {edit ? 'Cancel' : 'Edit'}
      </button>

      {edit && (
        <button
          onClick={saveeditemployee}
          className="bg-indigo-500 hover:bg-indigo-600 px-4 py-2 rounded-lg font-medium"
        >
          Save Changes
        </button>
      )}
    </div>

  </div>
)
}

export default Employeedetail
