'use client'

import { useEffect, useRef, useCallback } from 'react'
import Editor, { OnMount } from '@monaco-editor/react'
import * as monaco from 'monaco-editor'
import { useEditorStore } from '@/stores/editorStore'
import { useUIStore } from '@/stores/uiStore'
import { Loader2 } from 'lucide-react'

interface DocumentEditorProps {
  value: string
  onChange: (value: string) => void
  readOnly?: boolean
}

export function DocumentEditor({ value, onChange, readOnly = false }: DocumentEditorProps) {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null)
  const decorationsRef = useRef<string[]>([])
  const { setCursorPosition, updateCounts, setContent } = useEditorStore()
  const { editorSettings, theme } = useUIStore()

  // Function to update code block backgrounds
  const updateCodeBlockBackgrounds = useCallback((editor: monaco.editor.IStandaloneCodeEditor) => {
    const model = editor.getModel()
    if (!model) return

    const newDecorations: monaco.editor.IModelDeltaDecoration[] = []
    const lines = model.getLinesContent()
    let inCodeBlock = false

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()

      // Check for code block start/end (```)
      if (line === '```' || line.startsWith('```')) {
        inCodeBlock = !inCodeBlock
        // Add decoration to the fence line itself
        newDecorations.push({
          range: new monaco.Range(i + 1, 1, i + 1, 1),
          options: {
            isWholeLine: true,
            className: 'execution-code-line',
          },
        })
      } else if (inCodeBlock) {
        // Lines inside code blocks get gray background
        newDecorations.push({
          range: new monaco.Range(i + 1, 1, i + 1, 1),
          options: {
            isWholeLine: true,
            className: 'execution-code-line',
          },
        })
      }
    }

    decorationsRef.current = editor.deltaDecorations(decorationsRef.current, newDecorations)
  }, [])

  const handleEditorDidMount: OnMount = useCallback((editor, monaco) => {
    editorRef.current = editor

    // Configure PyMD language support
    monaco.languages.register({ id: 'pymd' })

    // Basic PyMD tokenization (can be enhanced later)
    monaco.languages.setMonarchTokensProvider('pymd', {
      tokenizer: {
        root: [
          // Headers
          [/^#{1,6}\s.*$/, 'keyword'],
          // Code blocks
          [/```[\s\S]*?```/, 'string'],
          // Inline code
          [/`[^`]*`/, 'string'],
          // Bold
          [/\*\*[^*]+\*\*/, 'emphasis'],
          // Italic
          [/\*[^*]+\*/, 'emphasis'],
          // Links
          [/\[([^\]]+)\]\(([^)]+)\)/, 'link'],
          // Python execution blocks (PyMD specific)
          [/\{\{[\s\S]*?\}\}/, 'number'],
          // Comments
          [/<!--[\s\S]*?-->/, 'comment'],
        ]
      }
    })

    // Update cursor position on selection change
    editor.onDidChangeCursorPosition((e) => {
      setCursorPosition({
        line: e.position.lineNumber,
        column: e.position.column
      })
    })

    // Update counts on content change
    editor.onDidChangeModelContent(() => {
      const content = editor.getValue()
      const wordCount = content.trim().split(/\s+/).filter(Boolean).length
      const charCount = content.length
      updateCounts(wordCount, charCount)
      updateCodeBlockBackgrounds(editor)
    })

    // Initial background update
    setTimeout(() => updateCodeBlockBackgrounds(editor), 100)
  }, [setCursorPosition, updateCounts, updateCodeBlockBackgrounds])

  const handleChange = useCallback((value: string | undefined) => {
    const newValue = value || ''
    onChange(newValue)
    setContent(newValue)
  }, [onChange, setContent])

  // Apply editor settings when they change
  useEffect(() => {
    if (editorRef.current) {
      editorRef.current.updateOptions({
        fontSize: editorSettings.fontSize,
        lineHeight: editorSettings.lineHeight,
        tabSize: editorSettings.tabSize,
        wordWrap: editorSettings.wordWrap ? 'on' : 'off',
        minimap: { enabled: editorSettings.minimap },
        lineNumbers: editorSettings.lineNumbers ? 'on' : 'off',
      })
    }
  }, [editorSettings])

  // Apply theme when it changes
  useEffect(() => {
    if (editorRef.current) {
      const monacoTheme = theme === 'light' ? 'vs' : 'vs-dark'
      editorRef.current.updateOptions({
        theme: monacoTheme,
      })
    }
  }, [theme])

  return (
    <div className="h-full w-full">
      <Editor
        height="100%"
        defaultLanguage="pymd"
        language="pymd"
        value={value}
        onChange={handleChange}
        onMount={handleEditorDidMount}
        theme={theme === 'light' ? 'vs' : 'vs-dark'}
        options={{
          readOnly,
          fontSize: editorSettings.fontSize,
          lineHeight: editorSettings.lineHeight,
          tabSize: editorSettings.tabSize,
          wordWrap: editorSettings.wordWrap ? 'on' : 'off',
          minimap: { enabled: editorSettings.minimap },
          lineNumbers: editorSettings.lineNumbers ? 'on' : 'off',
          automaticLayout: true,
          scrollBeyondLastLine: false,
          folding: true,
          renderWhitespace: 'selection',
          bracketPairColorization: { enabled: true },
          suggest: {
            showKeywords: true,
            showSnippets: true,
          },
        }}
        loading={
          <div className="flex h-full items-center justify-center">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        }
      />
    </div>
  )
}
