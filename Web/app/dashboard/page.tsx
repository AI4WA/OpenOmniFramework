'use client'
// pages/dashboard.js
import Image from 'next/image';
import Link from 'next/link';
import Header from "@/components/Header";
import React from "react"; // Make sure the import path is correct

export default function Dashboard() {
    return (
        <div>
            <Header/>
            <div className="flex min-h-screen flex-col bg-gray-50 dark:bg-gray-900">
                <main className="flex-grow">
                    <div className="text-center py-10">
                        <h1 className="text-5xl font-bold text-gray-800 dark:text-white">
                            Dashboard
                        </h1>
                        <p className="mt-3 text-lg text-gray-600 dark:text-gray-300">
                            Explore the features of our platform.
                        </p>
                    </div>
                    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 px-5 md:px-10 lg:px-20">
                        {/* Open Source LLM Evaluation */}
                        <Link href="/tasks">
                            <div
                                className="block rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800 cursor-pointer">
                                <div className="flex flex-col items-center">
                                    <Image src="/icons/task.svg" alt="Open Source LLM Evaluation" width={64}
                                           height={64}/>
                                    <h3 className="mt-5 text-xl font-semibold text-gray-800 dark:text-white">
                                        Open Source LLM Evaluation
                                    </h3>
                                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                                        Manage your evaluation tasks and view results.
                                    </p>
                                </div>
                            </div>
                        </Link>
                        {/* Chat with Open Source LLM */}
                        <Link href="/chat">
                            <div
                                className="block rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800 cursor-pointer">
                                <div className="flex flex-col items-center">
                                    <Image src="/icons/chat.svg" alt="Chat with Open Source LLM" width={64}
                                           height={64}/>
                                    <h3 className="mt-5 text-xl font-semibold text-gray-800 dark:text-white">
                                        Chat with Open Source LLM
                                    </h3>
                                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                                        Engage with Open Source LLM models.
                                    </p>
                                </div>
                            </div>
                        </Link>
                        <Link href="/jarv5">
                            <div
                                className="block rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800 cursor-pointer">
                                <div className="flex flex-col items-center">
                                    <Image src="/icons/JARV5.webp" alt="Chat with Open Source LLM" width={64}
                                           height={64}/>
                                    <h3 className="mt-5 text-xl font-semibold text-gray-800 dark:text-white">
                                        J.A.R.V.5
                                    </h3>
                                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                                        Aged Care Robot
                                    </p>
                                </div>
                            </div>
                        </Link>

                        <div
                            className="block rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800 cursor-pointer">
                            <div className="flex flex-col items-center">
                                <Image src="/icons/more.svg" alt="Chat with Open Source LLM" width={64}
                                       height={64}/>
                                <h3 className="mt-5 text-xl font-semibold text-gray-800 dark:text-white">
                                    More to come...
                                </h3>
                                <p className="mt-2 text-sm text-gray-600 dark:text-gray-300">
                                    If you have some ideas, we can work together!
                                </p>
                            </div>
                        </div>

                    </div>
                </main>

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
        </div>
    );
}
