import React from 'react'
import { Route, Routes } from 'react-router-dom'
import Mainpage from './pages/Mainpage'
import {Toaster} from 'react-hot-toast'
const App = () => {
  return (
    <div >

     <Routes>
      <Route path='/' element={<Mainpage/>} />
     </Routes>
     <Toaster/>
    </div>
  )
}

export default App