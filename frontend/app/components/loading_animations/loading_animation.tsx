'use client';

import styles from './loading.module.css';

const LoadingAnimation = () => {
  return (
    <div className={styles.container}>
      <svg className={styles.pl} viewBox="0 0 128 128" width="128px" height="128px" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="pl-grad" x1={0} y1={0} x2={0} y2={1}>
            <stop offset="0%" stopColor="hsl(193,90%,55%)" />
            <stop offset="100%" stopColor="hsl(223,90%,55%)" />
          </linearGradient>
        </defs>
        <circle className={styles.pl__ring} r={56} cx={64} cy={64} fill="none" strokeWidth={16} strokeLinecap="round" />
        <path className={styles.pl__worm} d="M92,15.492S78.194,4.967,66.743,16.887c-17.231,17.938-28.26,96.974-28.26,96.974L119.85,59.892l-99-31.588,57.528,89.832L97.8,19.349,13.636,88.51l89.012,16.015S81.908,38.332,66.1,22.337C50.114,6.156,36,15.492,36,15.492a56,56,0,1,0,56,0Z" fill="none" stroke="url(#pl-grad)" strokeWidth={16} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="44 1111" strokeDashoffset={10} />
      </svg>
    </div>
  );
}

export default LoadingAnimation;


// const Loader = () => {
//   return (
//     <nStyledWrapper>
//       <div className="terminal-loader">
//         <div className="terminal-header">
//           <div className="terminal-title">Status</div>
//           <div className="terminal-controls">
//             <div className="control close" />
//             <div className="control minimize" />
//             <div className="control maximize" />
//           </div>
//         </div>
//         <div className="text">Loading...</div>
//       </div>
//     </nStyledWrapper>
//   );
// }

// const nStyledWrapper = styled.div`
//   @keyframes blinkCursor {
//     50% {
//       border-right-color: transparent;
//     }
//   }

//   @keyframes typeAndDelete {
//     0%,
//     10% {
//       width: 0;
//     }
//     45%,
//     55% {
//       width: 6.2em;
//     } /* adjust width based on content */
//     90%,
//     100% {
//       width: 0;
//     }
//   }

//   .terminal-loader {
//     border: 0.1em solid #333;
//     background-color: #1a1a1a;
//     color: #0f0;
//     font-family: "Courier New", Courier, monospace;
//     font-size: 1em;
//     padding: 1.5em 1em;
//     width: 12em;
//     box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
//     border-radius: 4px;
//     position: relative;
//     overflow: hidden;
//     box-sizing: border-box;
//   }

//   .terminal-header {
//     position: absolute;
//     top: 0;
//     left: 0;
//     right: 0;
//     height: 1.5em;
//     background-color: #333;
//     border-top-left-radius: 4px;
//     border-top-right-radius: 4px;
//     padding: 0 0.4em;
//     box-sizing: border-box;
//   }

//   .terminal-controls {
//     float: right;
//   }

//   .control {
//     display: inline-block;
//     width: 0.6em;
//     height: 0.6em;
//     margin-left: 0.4em;
//     border-radius: 50%;
//     background-color: #777;
//   }

//   .control.close {
//     background-color: #e33;
//   }

//   .control.minimize {
//     background-color: #ee0;
//   }

//   .control.maximize {
//     background-color: #0b0;
//   }

//   .terminal-title {
//     float: left;
//     line-height: 1.5em;
//     color: #eee;
//   }

//   .text {
//     display: inline-block;
//     white-space: nowrap;
//     overflow: hidden;
//     border-right: 0.2em solid green; /* Cursor */
//     animation:
//       typeAndDelete 4s steps(11) infinite,
//       blinkCursor 0.5s step-end infinite alternate;
//     margin-top: 1.5em;
//   }`;

// export Loader;

