'use client'

import React from "react";
import Header from "@/components/Header";

const Jarv5 = () => {
    return (
        <div style={{display: 'flex', flexDirection: 'column', height: '100vh'}}> {/* Step 1 & 2 */}
            <Header/>
            <div style={{flexGrow: 1}}> {/* Step 3 */}
                <h1>Jarv5</h1>
            </div>

            <footer className="bg-gray-800 text-white text-center p-4">
                <p>Developed by
                    <a href="https://www.linkedin.com/in/pascalsun23/" target="_blank" rel="noopener noreferrer"
                       className="text-blue-400 hover:text-blue-300 mx-1">
                        Pascal Sun
                    </a>
                    supported by
                    <a href="https://nlp-tlp.org/" target="_blank" rel="noopener noreferrer"
                       className="text-blue-400 hover:text-blue-300 mx-1">
                        UWA NLP-TLP GROUP
                    </a>
                </p>
            </footer>
        </div>
    )
}

export default Jarv5;
