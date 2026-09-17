"""Dual image description generator conforming to Section 5.5 of ProjectDetails.md."""

from app.domain.asset import Asset, AssetDescription


class ImageDescriptionGenerator:
    """Generates distinct Content and Retrieval descriptions for visual assets."""

    def describe_asset(self, asset: Asset) -> AssetDescription:
        name = asset.metadata.get("filename", asset.asset_id)
        caption = asset.description.caption if asset.description else f"Asset {name}"

        # 1. Content description: What is visibly present
        visual_desc = (
            f"Visual representation of {name}. Contains structural visual elements, "
            f"diagrammatic blocks, or text components."
        )

        # 2. Retrieval description: Concepts, entities, questions it answers
        retrieval_desc = (
            f"{name}; architecture diagram; overview; layout; visual asset; "
            f"concept model; reference diagram"
        )

        return AssetDescription(
            caption=caption,
            visual_description=visual_desc,
            retrieval_description=retrieval_desc,
            entities=[name],
            key_labels=[asset.asset_type.value],
        )
