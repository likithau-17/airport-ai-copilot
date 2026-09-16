# LAX Airport Pricing Policy

## Airport Code
LAX

## Surge Pricing
- The standard surge multiplier is 1.0x.
- Surge pricing may be considered when passenger demand significantly exceeds available driver supply.
- Surge multipliers below 1.3x require operational review before activation.
- Surge multipliers of 1.3x or higher require explicit human approval.
- Every pricing change must be recorded with the airport code, reason, timestamp, and approved multiplier.

## Pricing Limits
- The AI assistant must not independently activate high-impact pricing changes.
- The maximum temporary surge multiplier permitted by this policy is 2.0x.
- Requests above 2.0x must be rejected and escalated for policy review.

## Monitoring
- Pricing decisions should consider request volume, active drivers, queue size, and completion rate.
- Pricing changes should be reviewed when airport demand returns to normal levels.
