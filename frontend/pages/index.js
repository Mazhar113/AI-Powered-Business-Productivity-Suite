
import { useSession, signIn, signOut } from 'next-auth/react'
import axios from 'axios'
import { useState } from 'react'

export default function Home(){
  const { data: session } = useSession()
  const [q, setQ] = useState('')
  const [ans, setAns] = useState(null)

  async function ask(){
    const res = await axios.post(`${process.env.NEXT_PUBLIC_API_BASE||'http://localhost:8000'}/query_corporate_memory`, {question: q, k:3})
    setAns(res.data)
  }

  return (
    <div style={{padding:20, fontFamily:'system-ui'}}>
      <h1>AI Corporate Suite — Frontend demo</h1>
      {!session && <button onClick={() => signIn()}>Sign in</button>}
      {session && <div>
        <div>Signed in as {session.user.email} <button onClick={() => signOut()}>Sign out</button></div>
        <hr />
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Ask corporate memory..." style={{width:600}}/>
        <button onClick={ask}>Ask</button>
        <pre>{JSON.stringify(ans, null, 2)}</pre>
      </div>}
    </div>
  )
}
