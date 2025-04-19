import { useState, useEffect, useRef } from "react";

interface LogStreamProps {
    streamUrl: string;
    postLogAction?: ()=>void;
}

export const LogStream: React.FC<LogStreamProps> = ({streamUrl, postLogAction }) =>{
    const [messages, setMessages] = useState<string[]>([]);
    console.log(streamUrl)
    const bottomRef = useRef<HTMLDivElement | null>(null); 
    
    useEffect(()=>{
        if(streamUrl){
            fetchStream();
            if(postLogAction){
                postLogAction();
            }
        }
    }, [streamUrl])

    
    const fetchStream = async () => {
        const response = await fetch(`${streamUrl}`);
        console.log(response)
        const reader = response?.body?.getReader();
        const decoder = new TextDecoder('utf-8');
        console.log(reader)
        
  
        while (true) {
            let result = await reader?.read();
            if (result) {
                const { done, value } = result;
            // use `done` and `value` here

            if (done) break;
  
            const chunk = decoder.decode(value);
            setMessages((prev) => [...prev,chunk]);
          }
        }
      };


      useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' }); // 👈 Scroll when output updates
      }, [messages]);

    return (
        <div ref={bottomRef}  className="bg-black gap-2 p-4 text-white h-180 text-lg flex flex-wrap overflow-auto whitespace-normal break-words" >
            {messages.map((log, i) => (
                    <div ref={bottomRef} key={i}>{log}<br/></div>       
                )
            )}
        </div>
      );
  }