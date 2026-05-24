import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeHighlight from 'rehype-highlight'
import rehypeSlug from 'rehype-slug'
import 'highlight.js/styles/github.min.css'

export default function ReportMarkdown({ content }: { content: string }) {
  return (
    <div className="prose-report">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSlug, rehypeHighlight]}
        components={{
          a: ({ href, children, ...props }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" {...props}>
              {children}
            </a>
          ),
          table: ({ children }) => (
            <div className="report-table-wrap">
              <table>{children}</table>
            </div>
          ),
          thead: ({ children }) => <thead>{children}</thead>,
          img: ({ alt, ...props }) => (
            <img alt={alt} className="report-img" loading="lazy" {...props} />
          ),
          hr: () => <hr className="report-hr" />,
          blockquote: ({ children }) => (
            <blockquote className="report-blockquote">{children}</blockquote>
          ),
          pre: ({ children }) => <pre className="report-pre">{children}</pre>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
