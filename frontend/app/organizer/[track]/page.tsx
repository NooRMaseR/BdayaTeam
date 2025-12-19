
export default async function OrganizerTrackPage({params}: {params: Promise<{track: string}>}) {
    const resolved_props = await params
  return (
      <h1>Track { resolved_props.track }</h1>
  )
}
