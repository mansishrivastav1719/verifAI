import React from 'react';
import { FaShieldAlt } from 'react-icons/fa';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-sm py-3">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <FaShieldAlt className="text-2xl text-purple-600" />
            <span className="text-xl font-bold text-gray-800">verifAi</span>
          </div>
          
          <div className="hidden md:flex space-x-6">
            <a href="#upload" className="text-purple-600 font-medium hover:text-purple-800">Detect</a>
            <a href="#features" className="text-gray-600 hover:text-purple-600">How It Works</a>
            <a href="#requirements" className="text-gray-600 hover:text-purple-600">Requirements</a>
            <a href="#team" className="text-gray-600 hover:text-purple-600">Team</a>
          </div>
          
          <button className="md:hidden">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
