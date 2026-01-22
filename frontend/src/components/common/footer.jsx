import React from 'react';
import { FaGithub, FaLinkedin, FaTwitter, FaHackathon } from 'react-icons/fa';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-white pt-10 pb-6 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">V</span>
              </div>
              <span className="text-xl font-bold">verifAi</span>
            </div>
            <p className="text-gray-400 mb-4">
              AI-powered document forgery detection with explainable forensic analysis.
            </p>
            <div className="flex space-x-4">
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" 
                 className="text-gray-400 hover:text-white transition-colors">
                <FaGithub className="text-xl" />
              </a>
              <a href="https://twitter.com" target="_blank" rel="noopener noreferrer"
                 className="text-gray-400 hover:text-white transition-colors">
                <FaTwitter className="text-xl" />
              </a>
              <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer"
                 className="text-gray-400 hover:text-white transition-colors">
                <FaLinkedin className="text-xl" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li><a href="#upload" className="text-gray-400 hover:text-white transition-colors">Document Detection</a></li>
              <li><a href="#features" className="text-gray-400 hover:text-white transition-colors">How It Works</a></li>
              <li><a href="#requirements" className="text-gray-400 hover:text-white transition-colors">Requirements</a></li>
              <li><a href="#team" className="text-gray-400 hover:text-white transition-colors">Our Team</a></li>
            </ul>
          </div>

          {/* Features */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Features</h4>
            <ul className="space-y-2">
              <li className="flex items-center text-gray-400">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Error Level Analysis
              </li>
              <li className="flex items-center text-gray-400">
                <span className="w-2 h-2 bg-yellow-500 rounded-full mr-2"></span>
                OCR Text Analysis
              </li>
              <li className="flex items-center text-gray-400">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                Metadata Forensics
              </li>
              <li className="flex items-center text-gray-400">
                <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                Heatmap Visualization
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Support</h4>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Documentation</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">API Reference</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Us</a></li>
              <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Report Bug</a></li>
            </ul>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-800 my-8"></div>

        {/* Bottom Section */}
        <div className="text-center">
          <div className="flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-8 mb-4">
            <div className="flex items-center space-x-2 text-purple-300">
              <FaHackathon className="text-xl" />
              <span className="font-medium">Built for HackTheWinter 2024</span>
            </div>
            <div className="hidden md:block w-1 h-1 bg-gray-700 rounded-full"></div>
            <div>
              <span className="text-gray-400">Track: </span>
              <span className="text-green-300 font-medium">ML-103: Explainable Document Forgery Detection</span>
            </div>
          </div>
          
          <p className="text-gray-500 text-sm mb-2">
            ⚡ 24-hour Hackathon Project • All mandatory requirements implemented
          </p>
          
          <p className="text-gray-600 text-sm">
            © {currentYear} verifAi. All rights reserved. | Made with ❤️ for the community
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
