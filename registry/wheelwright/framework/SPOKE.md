# Wheelwright / Framework

**Node Path:** wheelwright/framework
**Type:** spoke
**Status:** active

## Location

Spoke files live at: `WAI-Spoke/` (repo root)
Manifest: `WAI-Spoke/WAI-Manifest.yaml`

## Purpose

Core framework implementation — CLI, templates, skills, and agent tools.
This node is also the source of truth for all framework templates pushed to other spokes.

## Notes

This spoke is unique: the framework repo IS the framework.
It dogfoods its own WAI-Spoke for session continuity while simultaneously
defining the templates that ship to all other spokes.
