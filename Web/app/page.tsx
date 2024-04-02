import Image from "next/image";

export default function Home() {
    return (
        <div className="flex min-h-screen flex-col">
            <main className="flex flex-col items-center justify-center p-24 bg-gray-50 dark:bg-gray-900 flex-grow">
                <div className="mb-10 text-center">
                    <h1 className="text-5xl font-bold text-gray-800 dark:text-white">
                        WA LLM Platform
                    </h1>
                    <p className="mt-4 text-lg text-gray-600 dark:text-gray-300">
                        Evaluate and interact with state-of-the-art Large Language Models (LLM) freely and easily.
                    </p>
                </div>
                <div className="grid gap-10 md:grid-cols-2 lg:grid-cols-4">
                    <a
                        className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800"
                    >
                        <Image src="/icons/upload.svg" alt="Upload CSV" width={64} height={64}/>
                        <h3 className="mt-5 mb-2 text-xl font-semibold text-gray-800 dark:text-white">
                            Upload Data
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                            Easily upload your CSV files for analysis and evaluation.
                        </p>
                    </a>

                    <a
                        className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800"

                    >
                        <Image src="/icons/evaluate.svg" alt="Evaluate" width={64} height={64}/>
                        <h3 className="mt-5 mb-2 text-xl font-semibold text-gray-800 dark:text-white">
                            Evaluate
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                            Perform evaluations and get insights directly on the platform.
                        </p>
                    </a>
                    <a href="/login" className="flex items-center">
                        <div
                            className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 bg-blue-600 hover:bg-blue-700 transition-colors">
                            <Image src="/icons/login.svg" alt="Evaluate" width={64} height={64}/>
                            <button className="text-white text-xl font-semibold">
                                Login / Register
                            </button>
                            <p className="mt-2 text-sm text-blue-200">
                                Access your personalized dashboard for more features.
                            </p>
                        </div>
                    </a>
                    <a
                        className="flex flex-col items-center justify-center rounded-lg border border-transparent p-6 transition-colors hover:border-gray-300 hover:bg-gray-100 dark:hover:border-neutral-700 dark:hover:bg-neutral-800"
                    >
                        <Image src="/icons/wa.png" alt="Western Australia" width={64} height={64}/>
                        <h3 className="mt-5 mb-2 text-xl font-semibold text-gray-800 dark:text-white">
                            Together
                        </h3>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                            Build the future of WA.
                        </p>
                    </a>
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
    );
}
