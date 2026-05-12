import axios from 'axios'
import React, { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { PlusCircleIcon, BotIcon } from 'lucide-react'
import Addemployee from './Addemployee'
import Employeedetail from './Employeedetail'
import Agentchat from './Agentchat'
import { motion, AnimatePresence } from 'framer-motion'

const Mainpage = () => {
    const [employees, setemployees] = useState([])
    const [showaddemployee, setshowaddemployee] = useState(false)
    const [showemployeedetail, setshowemployeedetail] = useState(false)
    const [employeeid, setemployeeid] = useState('')
    const [searchterm, setsearchterm] = useState('')
    const [showbot, setshowbot] = useState(false)

    useEffect(() => {
        const fetchemployees = async () => {
            try {
                const response = await axios.get("http://localhost:8080/api/allemployees")
                setemployees(response.data)
            } catch (error) {
                toast.error("Couldn't get employees")
            }
        }
        fetchemployees()
    }, [])

    const filteredemployees = employees.filter(employee => {
        const search = searchterm.toLowerCase()
        return (
            employee.firstname.toLowerCase().includes(search) ||
            employee.lastname.toLowerCase().includes(search)
        )
    })

    return (
        <div className='bg-[#0F172A] min-h-screen text-[#E2E8F0]'>

            {/* 🔷 HEADER */}
            <div className='bg-[#1E293B] border-b border-[#334155] px-6 py-4 flex justify-between items-center sticky top-0 z-10'>
                <h1 className='text-2xl font-bold tracking-wide'>
                    Employee Dashboard
                </h1>

                <div className='flex gap-3'>
                    <button 
                        onClick={() => setshowaddemployee(true)}
                        className='flex items-center gap-2 bg-[#6366F1] hover:bg-[#4F46E5] px-4 py-2 rounded-xl transition shadow-md'
                    >
                        <PlusCircleIcon size={18}/> Add
                    </button>

                    <button 
                        onClick={() => setshowbot(true)}
                        className='flex items-center gap-2 bg-[#22C55E] hover:bg-green-600 px-4 py-2 rounded-xl transition shadow-md'
                    >
                        <BotIcon size={18}/> Agent
                    </button>
                </div>
            </div>

            {/* 🔍 SEARCH */}
            <div className='p-4'>
                <input
                    type="text"
                    value={searchterm}
                    onChange={(e)=>setsearchterm(e.target.value)}
                    placeholder="Search employees..."
                    className='w-full p-3 rounded-xl bg-[#1E293B] border border-[#334155] focus:outline-none focus:ring-2 focus:ring-[#6366F1]'
                />
            </div>

            {/* 🧑‍💼 EMPLOYEE GRID */}
            <div className='grid lg:grid-cols-3 md:grid-cols-2 gap-4 p-4'>
                {filteredemployees.length > 0 ? (
                    filteredemployees.map((employee) => (
                        <motion.div
                            key={employee.id}
                            whileHover={{ scale: 1.04 }}
                            whileTap={{ scale: 0.97 }}
                            className='bg-[#1E293B] border border-[#334155] rounded-xl p-4 shadow-md cursor-pointer hover:border-[#6366F1] hover:shadow-lg transition'
                            onClick={() => {
                                setemployeeid(employee.id)
                                setshowemployeedetail(true)
                            }}
                        >
                            <div className='font-semibold text-lg'>
                                {employee.firstname} {employee.lastname}
                            </div>
                            <div className='text-[#94A3B8]'>{employee.email}</div>

                            <div className='mt-2 text-sm'>
                                <span className='text-[#22C55E]'>
                                    {employee.gender}
                                </span>
                            </div>

                            <div className='text-sm text-[#94A3B8]'>
                                {employee.phoneNumber}
                            </div>
                        </motion.div>
                    ))
                ) : (
                    <div className='col-span-3 text-center text-[#94A3B8] mt-10'>
                        No employees found
                    </div>
                )}
            </div>

            {/* 🔥 ANIMATED PANELS */}
            <AnimatePresence>

                {/* ➕ ADD EMPLOYEE PANEL */}
                {showaddemployee && (
                    <>
                        {/* backdrop */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className='fixed inset-0 bg-black/50 backdrop-blur-sm z-40'
                            onClick={() => setshowaddemployee(false)}
                        />

                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', stiffness: 120 }}
                            className='fixed top-0 right-0 w-full md:w-[400px] h-full bg-[#1E293B] z-50 shadow-2xl'
                        >
                            <Addemployee 
                                setemployees={setemployees} 
                                setshowaddemployee={setshowaddemployee}
                            />
                        </motion.div>
                    </>
                )}

                {/* 👤 EMPLOYEE DETAIL PANEL */}
                {showemployeedetail && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className='fixed inset-0 bg-black/50 backdrop-blur-sm z-40'
                            onClick={() => setshowemployeedetail(false)}
                        />

                        <motion.div
                            initial={{ x: '100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '100%' }}
                            transition={{ type: 'spring', stiffness: 120 }}
                            className='fixed top-0 right-0 w-full md:w-[400px] h-full bg-[#1E293B] z-50 shadow-2xl'
                        >
                            <Employeedetail
                                setemployees={setemployees}
                                setshowemployeedetail={setshowemployeedetail}
                                employeeid={employeeid}
                            />
                        </motion.div>
                    </>
                )}

                {/* 🤖 AGENT CHAT PANEL */}
{showbot && !showemployeedetail&& !showaddemployee &&(
    <motion.div
        initial={{ y: '100%' }}
        animate={{ y: 0 }}
        exit={{ y: '100%' }}
        transition={{ type: 'spring', stiffness: 120, damping: 20 }}
        className='fixed bottom-0 left-0 w-full z-50'
    >
        <Agentchat  
            setshowbot={setshowbot}
            setsearchterm={setsearchterm}
            setshowaddemployee={setshowaddemployee}
            setemployees={setemployees}
            setshowemployeedetail={setshowemployeedetail}
            setemployeeid={setemployeeid}
        />
    </motion.div>
)}
               

            </AnimatePresence>

        </div>
    )
}

export default Mainpage