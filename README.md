# Cloud Engineering Agents

## Project Overview

Cloud Engineering Agents is a comprehensive framework for managing multi-cloud infrastructure and automation through AI-powered agents. This repository provides tools, templates, and best practices for cloud engineering tasks across AWS, Azure, Google Cloud Platform, and administrative tools like Jira.

### Purpose

- Standardize cloud engineering workflows
- Accelerate infrastructure provisioning and management
- Provide reusable templates for common cloud operations
- Document best practices and lessons learned
- Enable efficient multi-cloud agent collaboration
- Manage administrative tools integration (Jira, etc.)

### Key Features

- Multi-cloud support (AWS, Azure, GCP)
- Administrative tools integration (Jira)
- Standardized prompt templates for agent interactions
- Session management and context tracking
- Integrated safety checks and validation protocols
- Cost optimization guidelines
- Security-first approach

## Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Cloud provider CLI tools (as needed):
  - AWS CLI
  - Azure CLI
  - gcloud CLI
- Administrative tool access:
  - Jira API credentials (when needed)

### Initial Setup

1. Clone the repository:
   ```bash
   cd /Users/nicksimmonds/code/cloud-engineering-agents
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies (when available):
   ```bash
   pip install -r requirements.txt
   ```

4. Configure cloud provider credentials:
   - AWS: `aws configure`
   - Azure: `az login`
   - GCP: `gcloud auth login`

### First Time Setup

1. Review `bootstrap.md` for agent interaction guidelines
2. Create your personal `project_context.md` for session tracking
3. Create `.onboard` file with your specific context and preferences

## Usage

### Starting a New Session

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate
   ```

2. Review `project_context.md` for current state
3. Update session information
4. Follow startup rules in `bootstrap.md`

### Working with Agents

1. Use prompt templates from `bootstrap.md`
2. Follow the three startup rules:
   - Always use venv for Python
   - Sanity check all agent output
   - Ask before creating artifacts

3. Document decisions and learnings in `project_context.md`

### Example Workflow

```bash
# Activate environment
source venv/bin/activate

# Review context
cat project_context.md

# Work with agents using bootstrap guidelines
# ... perform cloud engineering tasks ...

# Update context with learnings
# Edit project_context.md with session outcomes
```

## Repository Structure

```
cloud-engineering-agents/
├── .git/                    # Git repository data
├── .gitignore              # Git ignore patterns
├── bootstrap.md            # Agent startup rules and prompt templates
├── project_context.md      # Session info and lessons (gitignored)
├── .onboard                # Personal onboarding context (gitignored)
├── tmp/                    # Temporary files (gitignored)
├── README.md               # This file
├── requirements.txt        # Python dependencies (to be added)
├── agents/                 # Agent scripts and utilities (to be added)
│   ├── aws/               # AWS-specific agents
│   ├── azure/             # Azure-specific agents
│   ├── gcp/               # GCP-specific agents
│   └── admin/             # Administrative tool agents (Jira, etc.)
├── templates/              # Cloud-specific templates (to be added)
├── docs/                   # Additional documentation (to be added)
└── examples/               # Example prompts and workflows (to be added)
```

### Key Files

- **bootstrap.md**: Essential reading for all agent interactions. Contains startup rules, prompt templates, and guidelines.
- **project_context.md**: Your personal session tracker. Update this as you work to maintain context across sessions.
- **.onboard**: Personal file for your specific context, preferences, and onboarding notes.
- **README.md**: Project overview and documentation (this file).

## Contributing

### Guidelines

1. **Follow the Bootstrap Rules**
   - Use virtual environments
   - Sanity check all changes
   - Ask before creating new artifacts

2. **Documentation Standards**
   - Update README.md for structural changes
   - Document decisions in commit messages
   - Add examples for new templates
   - Keep bootstrap.md current with best practices

3. **Code Standards**
   - Follow PEP 8 for Python code
   - Include docstrings for all functions
   - Add type hints where applicable
   - Write tests for new functionality

4. **Cloud Resource Standards**
   - Always tag resources appropriately
   - Follow least-privilege principle
   - Document cost implications
   - Include rollback procedures

### Workflow

1. Create a feature branch
2. Make changes following guidelines
3. Update documentation
4. Test thoroughly
5. Submit pull request with clear description

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Example:
```
feat: Add AWS S3 bucket provisioning template

Added reusable template for creating S3 buckets with
security best practices including encryption, versioning,
and lifecycle policies.

Closes #123
```

## Best Practices

### Security
- Never commit credentials or secrets
- Use environment variables for sensitive data
- Follow cloud provider security best practices
- Implement least-privilege access controls
- Enable encryption by default

### Cost Management
- Estimate costs before provisioning resources
- Implement lifecycle policies for storage
- Use appropriate resource sizing
- Tag all resources for cost tracking
- Set up billing alerts

### Multi-Cloud Considerations
- Abstract cloud-specific implementations when possible
- Document provider-specific requirements
- Consider cross-cloud authentication patterns
- Plan for different pricing models

## Resources

### Documentation
- [AWS Documentation](https://docs.aws.amazon.com/)
- [Azure Documentation](https://docs.microsoft.com/azure/)
- [GCP Documentation](https://cloud.google.com/docs)
- [Jira API Documentation](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)

### Tools
- [Terraform](https://www.terraform.io/)
- [Ansible](https://www.ansible.com/)
- [Pulumi](https://www.pulumi.com/)

### Community
- GitHub Issues for bug reports and feature requests
- Discussions for questions and ideas

## License

[To be determined]

## Contact

Maintainer: Nick Simmonds

Email: c_nsimmonds@groupon.com

## Acknowledgments

This project leverages AI-powered agents to enhance cloud engineering workflows and productivity.

---

Last Updated: 2025-12-26
