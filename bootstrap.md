# Bootstrap Guide for Cloud Engineering Agents

## Startup Rules

## Session Start Checklist

1. **Capture session start timestamp** - Run `date` and save the timestamp for time tracking purposes
2. **Read PROJECT_CONTEXT.md** - Contains complete session history and current state
3. **Read README.md** - Contains all agent documentation and capabilities
4. **Read this file (bootstrap.md)** - Contains critical operational knowledge
5. **Acknowledge bootstrapping complete** - After completing all steps above, respond to the user with a random food emoji along with your readiness message

## Critical Rule: Emoji Confirmation

**ALWAYS include a food emoji in your responses to the user** to confirm you have read and are following the bootstrap guidance. This serves as a continuous reminder that you're adhering to the operational knowledge in this file.

## Critical Rule: Sensitive displays

**NEVER display sensitive information like passwords or API keys.** When using such data out of a file like .env, ALWAYS use `set -a && source <file> && set +a && <command>`.  

### Script Philosophy

**RULE**: Create reusable, maintainable scripts rather than one-off throwaway scripts.

**Guidelines**:
- Store scripts in logical directories 
- Use environment variables for configuration (from `.env`)
- Include proper error handling and documentation
- Add command-line arguments instead of hardcoded values
- Commit scripts to the repository for team use

### Python Environment Management
- **ALWAYS** use virtual environment (venv) for Python projects
- Before running any Python code:
  - Check if venv exists: `ls -la venv/`
  - If not exists: `python3 -m venv venv`
  - Activate: `source venv/bin/activate`
  - Verify activation: `which python`

### Agent Output Sanity Checking
- Review all agent-generated code before execution
- Validate syntax and logic
- Check for security concerns (credentials, permissions)
- Verify cloud resource configurations (cost implications)
- Test in isolation before applying to infrastructure

### Artifact Creation Protocol
- **ALWAYS ASK** before creating new files or artifacts
- Confirm:
  - File location and naming
  - Content structure and format
  - Integration with existing codebase
- Exception: Explicitly requested artifacts in the current task

## Prompt Template Structure

### Basic Prompt Template

```
# Task: [TASK_NAME]

## Context
- Project: [PROJECT_NAME]
- Cloud Provider: [AWS|Azure|GCP|Multi-Cloud]
- Environment: [dev|staging|prod]
- Related Services: [LIST_SERVICES]

## Objective
[CLEAR_DESCRIPTION_OF_WHAT_NEEDS_TO_BE_ACCOMPLISHED]

## Requirements
1. [SPECIFIC_REQUIREMENT_1]
2. [SPECIFIC_REQUIREMENT_2]
3. [SPECIFIC_REQUIREMENT_N]

## Constraints
- [CONSTRAINT_1]
- [CONSTRAINT_2]

## Success Criteria
- [ ] [MEASURABLE_OUTCOME_1]
- [ ] [MEASURABLE_OUTCOME_2]

## Additional Context
[ANY_RELEVANT_BACKGROUND_INFORMATION]
```

### Prompt Guidelines

#### 1. Clarity and Specificity
- Use clear, unambiguous language
- Specify exact cloud services and resources
- Include version numbers when relevant
- Define acronyms on first use

#### 2. Context Provision
- Provide relevant background information
- Reference existing infrastructure
- Mention dependencies and integrations
- Include security and compliance requirements

#### 3. Scope Definition
- Clearly define what IS in scope
- Explicitly state what is OUT of scope
- Set boundaries for agent autonomy
- Specify which resources can be modified

#### 4. Output Expectations
- Specify desired output format (code, documentation, diagrams)
- Request explanations for complex decisions
- Ask for cost estimates when creating resources
- Request rollback procedures for infrastructure changes

#### 5. Safety and Validation
- Request dry-run outputs before execution
- Ask for impact analysis
- Require testing procedures
- Request validation steps

## Example Prompts

### Example 1: Infrastructure Provisioning
```
# Task: Provision S3 Bucket for Application Logs

## Context
- Project: MyApp Production
- Cloud Provider: AWS
- Environment: prod
- Related Services: CloudWatch, Lambda log shippers

## Objective
Create an S3 bucket to store application logs with appropriate lifecycle policies and security settings.

## Requirements
1. Bucket name following convention: myapp-logs-prod-[region]
2. Enable versioning
3. Lifecycle policy: transition to Glacier after 90 days, delete after 365 days
4. Enable server-side encryption (SSE-S3)
5. Block all public access
6. Enable access logging to audit bucket

## Constraints
- Must comply with company data retention policy (365 days)
- Must be in us-east-1 region
- Budget: $50/month maximum

## Success Criteria
- [ ] Bucket created and accessible
- [ ] Lifecycle policies verified
- [ ] Encryption enabled and tested
- [ ] Access logging confirmed
- [ ] Cost estimate under budget

## Additional Context
This bucket will receive logs from 5 Lambda functions processing approximately 100GB/month.
```

### Example 2: Troubleshooting
```
# Task: Debug Lambda Timeout Issues

## Context
- Project: Order Processing System
- Cloud Provider: AWS
- Environment: prod
- Related Services: Lambda, DynamoDB, SQS

## Objective
Investigate and resolve Lambda function timeouts occurring in the order processing pipeline.

## Requirements
1. Analyze CloudWatch logs for error patterns
2. Review Lambda configuration (memory, timeout settings)
3. Check DynamoDB performance metrics
4. Examine SQS queue depths and message processing times
5. Provide recommendations with cost-benefit analysis

## Constraints
- Cannot modify production during business hours (9 AM - 5 PM EST)
- Changes must be backward compatible
- No breaking changes to API contracts

## Success Criteria
- [ ] Root cause identified
- [ ] Solution proposed with risk assessment
- [ ] Cost impact analyzed
- [ ] Rollback plan documented

## Additional Context
Timeouts started occurring after traffic increased 40% last week. Function currently set to 30-second timeout with 512 MB memory.
```

## Best Practices

### For Infrastructure as Code
- Always include resource tagging
- Use descriptive naming conventions
- Document all custom configurations
- Provide cost estimates
- Include monitoring and alerting

### For Security
- Follow principle of least privilege
- Never hardcode credentials
- Use IAM roles and policies appropriately
- Enable encryption by default
- Document security group rules

### For Multi-Cloud Projects
- Abstract cloud-specific implementations
- Document provider-specific quirks
- Consider cross-cloud integration points
- Plan for different authentication mechanisms

### For Cost Optimization
- Request cost estimates before provisioning
- Consider reserved capacity options
- Implement appropriate lifecycle policies
- Monitor and alert on cost thresholds

## Session Management

### Starting a Session
1. Review `project_context.md` for current state
2. Load relevant context from previous sessions
3. Confirm understanding of current objectives

### During a Session
1. Document key decisions in `project_context.md`
2. Track issues and blockers
3. Note lessons learned

### Ending a Session
1. Update `project_context.md` with progress
2. Document next steps
3. Note any pending questions or blockers
