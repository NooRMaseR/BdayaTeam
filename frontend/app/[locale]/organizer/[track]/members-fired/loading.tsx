import LoadingAnimation from '@/app/components/loading_animations/loading_animation';

export default function Loading() {
  return (
    <div className='flex w-full h-svh justify-center items-center'>
        <LoadingAnimation />
    </div>
  )
}
