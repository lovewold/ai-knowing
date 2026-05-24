import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import 'highlight.js/styles/github.min.css'

export default function ChatMarkdown({ content }: { content: string }) {
  return (
    <section className="prose-chat">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={{
          a: ({ href, children, ...props }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
              {children}
            </a>
          ),
          pre: ({ children }) => <pre className="prose-chat-pre">{children}</pre>,
        }}
      >
        {content}
      </ReactMarkdown>
    </section>
  )
}
