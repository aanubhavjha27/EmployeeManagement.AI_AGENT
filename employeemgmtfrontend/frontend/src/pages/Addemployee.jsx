
import axios from 'axios'
import { X } from 'lucide-react'
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

const Addemployee = (props) => {
  const [firstname, setfirstname] = useState('')
  const [lastname, setlastname] = useState('')
  const [email, setemail] = useState('')
  const [loading, setloading] = useState(false)

  const submit = async () => {
    if (!firstname || !lastname || !email) {
      toast.error('All fields are required')
      return
    }

    try {
      setloading(true)
      const response = await axios.post(
        'http://localhost:8080/api/addemployee',
        { firstname, lastname, email }
      )

      props.setemployees(prev => [response.data, ...prev])
      toast.success('Employee added successfully')
      props.setshowaddemployee(false)
    } catch (error) {
      if (error.response && error.response.status === 409) {
        toast.error('Email already exists')
      } else {
        toast.error('Something went wrong')
      }
    } finally {
      setloading(false)
    }
  }

 return (
  <div className="h-full w-full flex flex-col p-6 text-white bg-gradient-to-br from-slate-900 to-slate-800">

    {/* Header */}
    <div className="flex items-center mb-6">
      <h2 className="text-lg font-semibold">Add Employee</h2>
      <X
        className="ml-auto cursor-pointer hover:text-gray-300"
        onClick={() => props.setshowaddemployee(false)}
      />
    </div>

    {/* Form */}
    <div className="space-y-4">
      <input
        type="text"
        placeholder="First Name"
        value={firstname}
        onChange={(e) => setfirstname(e.target.value)}
        className="w-full p-2 rounded-lg bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <input
        type="text"
        placeholder="Last Name"
        value={lastname}
        onChange={(e) => setlastname(e.target.value)}
        className="w-full p-2 rounded-lg bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <input
        type="email"
        placeholder="Email Address"
        value={email}
        onChange={(e) => setemail(e.target.value)}
        className="w-full p-2 rounded-lg bg-white/10 border border-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
    </div>

    {/* Footer */}
    <button
      onClick={submit}
      disabled={loading}
      className="mt-auto bg-indigo-500 hover:bg-indigo-600 p-2 rounded-lg font-medium disabled:opacity-50"
    >
      {loading ? 'Adding...' : 'Add Employee'}
    </button>

  </div>
)
}

export default Addemployee

