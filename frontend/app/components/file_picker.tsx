import React from 'react';

interface FileProps {
    accept: `${string}/${string}`
}

export default function FilePicker({ accept, ...props }: FileProps & React.InputHTMLAttributes<HTMLInputElement>) {
  return (
      <div>
          <input type="file" accept={accept} {...props} />
      </div>
  )
}
